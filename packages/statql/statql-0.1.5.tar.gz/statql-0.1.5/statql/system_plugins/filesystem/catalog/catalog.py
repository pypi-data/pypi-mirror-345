import enum
import itertools
import os
import typing
from datetime import timedelta
from logging import getLogger

from pandas import DataFrame

from statql.common import ICatalog, StatQLInternalColumns, TableInfo
from ..common import FileSystemCatalogConfig, FileSystemIntegrationConfig

logger = getLogger(__name__)


class EntriesTableColumns(enum.StrEnum):
    PATH = "path"
    TYPE = "type"  # file/directory
    SIZE = "size"


FileSystemEntry = typing.Dict[EntriesTableColumns, typing.Any]


class FileSystemCatalog(ICatalog[FileSystemCatalogConfig, FileSystemIntegrationConfig, str]):
    def resolve_table_path(self, *, table_path: typing.Sequence[str]) -> typing.Generator[str, None, None]:
        if len(table_path) != 2:
            raise SyntaxError(f"Invalid table path, expected 2 parts")

        fs_name, table_name = table_path

        if fs_name == "?":
            roots = {integration.root_path for integration in self._integrations}

        else:
            roots = {integration.root_path for integration in self._integrations if integration.file_system_name == fs_name}

            if not roots:
                raise SyntaxError(f"File system integration not found: `{fs_name}`")

            if len(roots) > 1:
                raise RuntimeError(f"More than one file system found")

        yield from roots

    def scan_table(self, *, table: str, columns: typing.AbstractSet[str]) -> typing.Generator[DataFrame, None, None]:
        parsed_columns = self._parse_entries_table_columns(columns=columns)

        for chunk in itertools.batched(self._get_fs_entries(root_path=table, columns=parsed_columns), n=self._config.scan_chunk_size):
            yield DataFrame(chunk)

    @classmethod
    def _get_fs_entries(cls, *, root_path: str, columns: typing.AbstractSet[EntriesTableColumns]) -> typing.Generator[FileSystemEntry, None, None]:
        for root, dir_names, file_names in os.walk(root_path):
            for file_name in file_names:
                file_path = os.path.join(root, file_name)

                entry = {StatQLInternalColumns.ROW_ID: file_path}

                if EntriesTableColumns.PATH in columns:
                    entry[EntriesTableColumns.PATH] = file_path

                if EntriesTableColumns.SIZE in columns:
                    try:
                        entry[EntriesTableColumns.SIZE] = os.stat(file_path).st_size
                    except OSError:
                        entry[EntriesTableColumns.SIZE] = None

                if EntriesTableColumns.TYPE in columns:
                    entry[EntriesTableColumns.TYPE] = "file"

                yield entry

            for dir_name in dir_names:
                dir_path = os.path.join(root, dir_name)

                entry = {StatQLInternalColumns.ROW_ID: dir_path}

                if EntriesTableColumns.PATH in columns:
                    entry[EntriesTableColumns.PATH] = dir_path

                if EntriesTableColumns.SIZE in columns:
                    entry[EntriesTableColumns.SIZE] = 0

                if EntriesTableColumns.TYPE in columns:
                    entry[EntriesTableColumns.TYPE] = "directory"

                yield entry

    @classmethod
    def _parse_entries_table_columns(cls, *, columns: typing.Iterable[str]) -> typing.Set[EntriesTableColumns]:
        parsed_columns = set()

        for column in columns:
            try:
                parsed_columns.add(EntriesTableColumns(column))
            except ValueError as e:
                raise ValueError(f"Unknown `entries` table column: {column}") from e

        return parsed_columns

    def estimate_row_count(self, *, table: str) -> int:
        root_path = table

        try:
            return self._cache.fetch(key=f"fs.{root_path}.entries_count")
        except LookupError:
            logger.info(f"Fetching file system statistics...")

            fs_entries_count = sum(len(dirs) + len(files) for _, dirs, files in os.walk(root_path))
            self._cache.store(key=f"fs.{root_path}.entries_count", value=fs_entries_count, ttl=timedelta(hours=24))

            return fs_entries_count

    def fetch_all_tables(self, *, integration_config: FileSystemIntegrationConfig) -> typing.Generator[TableInfo, None, None]:
        yield TableInfo(
            path=(integration_config.file_system_name, "entries"),
            columns=set(EntriesTableColumns),
        )

    def close(self) -> None:
        pass
