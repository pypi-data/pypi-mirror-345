import asyncio
import logging
import typing
from datetime import timedelta

from statql.common import FrozenModel, CacheManager, safe_wait
from .client import PostgresClient
from .common import DatabaseIdentifier, PostgresTableInfo
from .connections_manager import PostgresConnectionsManager

logger = logging.getLogger(__name__)


class TableFilter(FrozenModel):
    cluster: str | None
    db: str | None
    schema: str | None
    table: str | None

    def matches_cluster(self, *, cluster_name: str) -> bool:
        return self.cluster is None or self.cluster == cluster_name

    def matches_db(self, *, db_name: str) -> bool:
        return self.db is None or self.db == db_name

    def matches_schema(self, *, schema_name: str) -> bool:
        return self.schema is None or self.schema == schema_name

    def matches_table(self, *, table_name: str) -> bool:
        return self.table is None or self.table == table_name


class Introspector:
    @classmethod
    async def introspect(
        cls,
        *,
        cluster_names: typing.Iterable[str],
        connections: PostgresConnectionsManager,
        cache: CacheManager,
        table_filter: TableFilter | None = None,
    ) -> typing.AsyncGenerator[PostgresTableInfo, None]:
        discovered_tables_q: asyncio.Queue[PostgresTableInfo] = asyncio.Queue()
        introspection_task = asyncio.create_task(
            cls._introspect_all(
                cluster_names=cluster_names, connections=connections, cache=cache, table_filter=table_filter, discovered_tables_q=discovered_tables_q
            )
        )

        try:
            while not (discovered_tables_q.empty() and introspection_task.done()):
                q_get_task = asyncio.create_task(discovered_tables_q.get())
                done, pending = await safe_wait([q_get_task, introspection_task], return_when=asyncio.FIRST_COMPLETED)

                if q_get_task in done:
                    yield q_get_task.result()

        finally:
            await introspection_task  # To raise errors

    @classmethod
    async def _introspect_all(
        cls,
        *,
        cluster_names: typing.Iterable[str],
        connections: PostgresConnectionsManager,
        cache: CacheManager,
        table_filter: TableFilter | None,
        discovered_tables_q: asyncio.Queue[PostgresTableInfo],
    ) -> None:
        await safe_wait(
            [
                asyncio.create_task(
                    cls._introspect_cluster(
                        cluster_name=cluster_name,
                        cache=cache,
                        connections=connections,
                        table_filter=table_filter,
                        discovered_tables_q=discovered_tables_q,
                    )
                )
                for cluster_name in cluster_names
                if table_filter is None or table_filter.matches_cluster(cluster_name=cluster_name)
            ],
            return_when=asyncio.ALL_COMPLETED,
        )

    @classmethod
    async def _introspect_cluster(
        cls,
        *,
        cluster_name: str,
        cache: CacheManager,
        connections: PostgresConnectionsManager,
        table_filter: TableFilter | None,
        discovered_tables_q: asyncio.Queue[PostgresTableInfo],
    ) -> None:
        try:
            db_names = await asyncio.to_thread(cache.fetch, key=f"pg.clusters.{cluster_name}.db_names")
        except LookupError:
            db_names = await PostgresClient.fetch_dbs_in_cluster(cluster_name=cluster_name, connections=connections)
            await asyncio.to_thread(cache.store, key=f"pg.clusters.{cluster_name}.db_names", value=db_names, ttl=timedelta(hours=24))

        await safe_wait(
            [
                asyncio.create_task(
                    cls._introspect_database(
                        db_identifier=DatabaseIdentifier(cluster_name=cluster_name, db_name=db_name),
                        cache=cache,
                        connections=connections,
                        table_filter=table_filter,
                        discovered_tables_q=discovered_tables_q,
                    )
                )
                for db_name in db_names
                if table_filter is None or table_filter.matches_db(db_name=db_name)
            ],
            return_when=asyncio.ALL_COMPLETED,
        )

    @classmethod
    async def _introspect_database(
        cls,
        db_identifier: DatabaseIdentifier,
        *,
        cache: CacheManager,
        connections: PostgresConnectionsManager,
        table_filter: TableFilter | None,
        discovered_tables_q: asyncio.Queue[PostgresTableInfo],
    ) -> None:
        try:
            cached_table_infos = await asyncio.to_thread(cache.fetch, key=f"pg.clusters.{db_identifier.cluster_name}.dbs.{db_identifier.db_name}.tables")
            table_infos = [PostgresTableInfo(**cached_table_info) for cached_table_info in cached_table_infos]

        except LookupError:
            table_infos = await PostgresClient.fetch_tables_in_db(db_identifier=db_identifier, connections=connections)
            await asyncio.to_thread(
                cache.store,
                key=f"pg.clusters.{db_identifier.cluster_name}.dbs.{db_identifier.db_name}.tables",
                value=[table_info.model_dump(mode="json") for table_info in table_infos],
                ttl=timedelta(hours=24),
            )

        for table_info in table_infos:
            if table_filter is None or (
                table_filter.matches_schema(schema_name=table_info.table_identifier.schema_name)
                and table_filter.matches_table(table_name=table_info.table_identifier.table_name)
            ):
                await discovered_tables_q.put(table_info)
