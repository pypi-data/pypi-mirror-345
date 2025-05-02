import asyncio
import typing
from asyncio import AbstractEventLoop
from concurrent.futures import ThreadPoolExecutor
from logging import getLogger
from queue import Queue, Empty

from statql.common import IAsyncCatalog, ICatalog, safe_wait, TableIdentifier
from ..common import (
    IPlanNode,
    StatQLContext,
    TableColumn,
    Term,
    PopulationPipelineBatch,
)

logger = getLogger(__name__)


class Scan(IPlanNode[PopulationPipelineBatch]):
    def __init__(
        self,
        *,
        catalog_name: str,
        table_path: typing.Sequence[str],
        columns: typing.AbstractSet[TableColumn],
    ):
        super().__init__()
        self._catalog_name = catalog_name
        self._table_path = table_path
        self._columns = columns

    def get_output_terms(self) -> typing.Set[Term]:
        return set(self._columns)

    def execute(self, *, ctx: StatQLContext) -> typing.Generator[PopulationPipelineBatch, None, None]:
        catalog = ctx.catalogs[self._catalog_name]

        if isinstance(catalog, IAsyncCatalog):
            scanner = AsyncScanner(catalog=catalog, event_loop=ctx.event_loop, table_path=self._table_path, columns=self._columns)
            yield from scanner.scan()

        elif isinstance(catalog, ICatalog):
            scanner = SyncScanner(catalog=catalog, table_path=self._table_path, columns=self._columns)
            yield from scanner.scan()

        else:
            raise TypeError(f"Unsupported catalog type: {type(catalog).__name__}")


class SyncScanner:
    def __init__(
        self,
        catalog: ICatalog,
        table_path: typing.Sequence[str],
        columns: typing.AbstractSet[TableColumn],
    ):
        self._catalog = catalog
        self._table_path = table_path
        self._columns = columns

        self._output_q = Queue()
        self._tables_being_scanned = set()
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._is_terminated = False

    def scan(self) -> typing.Generator[PopulationPipelineBatch, None, None]:
        with self._executor:
            dispatch_future = self._executor.submit(self._dispatch_tables)

            try:
                while True:
                    try:
                        yield self._output_q.get(timeout=1)
                    except Empty:
                        if dispatch_future.done() and not self._tables_being_scanned:
                            break
            finally:
                self._is_terminated = True
                self._executor.shutdown(wait=True, cancel_futures=True)

    def _dispatch_tables(self) -> None:
        try:
            for table_identifier in self._catalog.resolve_table_path(table_path=self._table_path):
                generator = self._scan_table(table=table_identifier)
                self._tables_being_scanned.add(table_identifier)
                self._executor.submit(self._get_item_from_gen, scan_table_gen=generator)

        except Exception as e:
            logger.exception(f"Dispatch failed: {e}")

    def _get_item_from_gen(self, *, scan_table_gen: typing.Generator[PopulationPipelineBatch, None, None]) -> None:
        try:
            batch = next(scan_table_gen)

        except StopIteration:
            pass

        except Exception as e:
            logger.exception(f"Error while scanning table: {e}")

        else:
            self._output_q.put(batch)
            self._executor.submit(self._get_item_from_gen, scan_table_gen=scan_table_gen)

    def _scan_table(self, *, table: TableIdentifier) -> typing.Generator[PopulationPipelineBatch, None, None]:
        try:
            estimated_size = self._catalog.estimate_row_count(table=table)
            column_rename_map = {col.column_name: str(hash(col)) for col in self._columns}

            for data in self._catalog.scan_table(table=table, columns={col.column_name for col in self._columns}):
                if self._is_terminated:
                    break

                # Fill in missing columns (StatQL is not strict in that sense since when querying multiple tables, you don't know if they differ in schema)
                for term in self._columns:
                    if term.column_name not in data.columns:
                        data[term.column_name] = None

                data.rename(columns=column_rename_map, inplace=True)

                yield PopulationPipelineBatch(data=data, table=table, table_estimated_size=estimated_size)

        finally:
            logger.debug(f"Table scan generator has exited: {table}")
            self._tables_being_scanned.remove(table)


class AsyncScanner:
    def __init__(
        self,
        *,
        catalog: IAsyncCatalog,
        event_loop: AbstractEventLoop,
        table_path: typing.Sequence[str],
        columns: typing.AbstractSet[TableColumn],
    ):
        self._catalog = catalog
        self._event_loop = event_loop
        self._table_path = table_path
        self._columns = columns

        self._output_q = Queue()
        self._is_terminated = False

    def scan(self) -> typing.Generator[PopulationPipelineBatch, None, None]:
        scan_all_tables_futures = asyncio.run_coroutine_threadsafe(self._scan_all_tables(), loop=self._event_loop)

        try:
            while True:
                try:
                    yield self._output_q.get(timeout=1)
                except Empty:
                    if scan_all_tables_futures.done():
                        break

        finally:
            self._is_terminated = True
            _ = scan_all_tables_futures.result()

    async def _scan_all_tables(self) -> None:
        await safe_wait(
            [asyncio.create_task(self._scan_table(table=table)) async for table in self._catalog.resolve_table_path(table_path=self._table_path)],
            return_when=asyncio.ALL_COMPLETED,
        )

    async def _scan_table(
        self,
        *,
        table: typing.Hashable,
    ) -> None:
        estimated_row_count = await self._catalog.estimate_row_count(table=table)
        column_rename_map = {col.column_name: str(hash(col)) for col in self._columns}

        async for data in self._catalog.scan_table(table=table, columns={col.column_name for col in self._columns}):
            if self._is_terminated:
                break

            # Fill in missing columns (StatQL is not strict in that sense since when querying multiple tables, you don't know if they differ in schema)
            for term in self._columns:
                if term.column_name not in data.columns:
                    data[term.column_name] = None

            data.rename(columns=column_rename_map, inplace=True)
            self._output_q.put(PopulationPipelineBatch(data=data, table=table, table_estimated_size=estimated_row_count))
