import asyncio
import os
import typing
from asyncio import AbstractEventLoop
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from logging import getLogger
from threading import Thread

from statql.common import CacheManager, ICatalog, IAsyncCatalog, async_gen_to_sync_gen, TableInfo
from .plugins_manager import PluginsManager
from .query_executor import QueryExecutor
from .query_planner import Planner
from .quey_parser import QueryParser
from ..common import AggregationPipelineBatch, StatQLContext, StatQLConfig

logger = getLogger(__name__)


class StatQLClient:
    def __init__(self, *, config: StatQLConfig):
        self._config = config

        # Populated after __enter__
        self._ctx: StatQLContext | None = None
        self._event_loop: AbstractEventLoop | None = None
        self._event_loop_runner: Thread | None = None

    def __enter__(self):
        catalogs = self._initialize_catalogs(config=self._config)

        # Some catalogs are implemented in asyncio, so we build an event loop
        self._event_loop = asyncio.new_event_loop()
        self._event_loop.set_default_executor(ThreadPoolExecutor(max_workers=10))

        self._event_loop_runner = Thread(target=self._event_loop.run_forever, name="statql_event_loop")
        self._event_loop_runner.start()

        self._ctx = StatQLContext(event_loop=self._event_loop, catalogs=catalogs)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close_catalogs(catalogs=self._ctx.catalogs.values(), loop=self._event_loop)
        self._event_loop.call_soon_threadsafe(self._event_loop.stop)
        self._event_loop_runner.join()

    @classmethod
    def _initialize_catalogs(cls, *, config: StatQLConfig) -> typing.Dict[str, ICatalog | IAsyncCatalog]:
        catalog_type_to_integrations = defaultdict(list)

        for integration in config.integrations.values():
            catalog_type_to_integrations[integration.catalog_name].append(integration.config)

        catalogs = {}

        for catalog_name, integrations in catalog_type_to_integrations.items():
            plugin = PluginsManager.get_plugin_by_catalog_name(catalog_name=catalog_name)
            catalog_config = config.catalog_name_to_config.get(catalog_name, plugin.catalog_config_cls())
            cache_manager = CacheManager(file_path=os.path.join(config.cache_dir_path, f"{catalog_name}.json"))
            catalog = plugin.catalog_cls(cache_manager=cache_manager, config=catalog_config, integrations=integrations)
            catalogs[catalog_name] = catalog

        return catalogs

    @classmethod
    def _close_catalogs(cls, *, catalogs: typing.Iterable[ICatalog | IAsyncCatalog], loop: AbstractEventLoop) -> None:
        for catalog in catalogs:
            try:
                if isinstance(catalog, ICatalog):
                    catalog.close()
                elif isinstance(catalog, IAsyncCatalog):
                    future = asyncio.run_coroutine_threadsafe(catalog.close(), loop=loop)
                    future.result(timeout=5)
                else:
                    raise TypeError(f"Unexpected catalog type: {type(catalog).__name__}")

            except Exception as e:
                logger.exception(f"Failed to close catalog: {e}")

    def query(self, *, sql: str) -> typing.Generator[AggregationPipelineBatch, None, None]:
        parsed_query = QueryParser.parse(sql=sql, ctx=self._ctx)
        execution_plan = Planner.plan(parsed_query=parsed_query)
        yield from QueryExecutor.execute(plan=execution_plan, ctx=self._ctx)

    def fetch_all_tables(self, *, integration_id: str) -> typing.Generator[TableInfo, None, None]:
        integration = self._config.integrations[integration_id]
        catalog = self._ctx.catalogs.get(integration.catalog_name)

        if not catalog:
            raise LookupError(f"Catalog is not in context: {integration.catalog_name}")

        if isinstance(catalog, ICatalog):
            gen = catalog.fetch_all_tables(integration_config=integration.config)

        elif isinstance(catalog, IAsyncCatalog):
            gen = async_gen_to_sync_gen(async_gen=catalog.fetch_all_tables(integration_config=integration.config), loop=self._ctx.event_loop)

        else:
            raise TypeError(f"Unexpected catalog type: {type(catalog).__name__}")

        for table_info in gen:
            # TODO: this is bad fix this
            table_info = TableInfo(path=[integration.catalog_name, *table_info.path], columns=table_info.columns)
            yield table_info
