import typing

from pandas import DataFrame

from statql.common import TableInfo, CacheManager, IAsyncCatalog, StatQLInternalColumns
from .client import RedisClient
from .common import RedisTableIdentifier, RedisDatabaseIdentifier, RedisTableNames, RedisKeysTableColumns
from .connections_manager import RedisConnectionsManager
from ..common import RedisCatalogConfig, RedisIntegrationConfig


class RedisCatalog(IAsyncCatalog[RedisCatalogConfig, RedisIntegrationConfig, RedisTableIdentifier]):
    def __init__(self, *, cache_manager: CacheManager, config: RedisCatalogConfig, integrations: typing.Iterable[RedisIntegrationConfig]):
        super().__init__(cache_manager=cache_manager, config=config, integrations=integrations)
        self._connections = RedisConnectionsManager(integrations=integrations)

    async def resolve_table_path(self, *, table_path: typing.Sequence[str]) -> typing.AsyncGenerator[RedisTableIdentifier, None]:
        if len(table_path) != 3:
            raise SyntaxError(f"Invalid table path: expected <cluster>.db<db>.<table>")  # TODO: this will be confusing because there are three parts actually

        cluster_name, db_id, table_name = table_path

        if cluster_name == "?":
            cluster_names = {integration.cluster_name for integration in self._integrations}
        else:
            if cluster_name not in {integration.cluster_name for integration in self._integrations}:
                raise SyntaxError(f"Unknown cluster name: {cluster_name}")

            cluster_names = {cluster_name}

        try:
            table_name = RedisTableNames(table_name)
        except ValueError as e:
            raise SyntaxError(f"Invalid table name, expected: {list(RedisTableNames)}") from e

        for cluster_name in cluster_names:
            conn = await self._connections.get_connection(db_identifier=RedisDatabaseIdentifier(cluster_name=cluster_name, db=0))
            num_databases = await RedisClient.get_db_count(conn=conn)

            if db_id == "?":
                # TODO - needed?
                for db_id in range(num_databases):
                    yield RedisTableIdentifier(cluster_name=cluster_name, db=db_id, table=table_name)

            else:
                try:
                    db_id = self._parse_db_id(db_id=db_id)
                except ValueError as e:
                    raise SyntaxError("Invalid DB ID") from e

                if db_id < num_databases:
                    yield RedisTableIdentifier(cluster_name=cluster_name, db=db_id, table=table_name)

    @classmethod
    def _parse_db_id(cls, *, db_id: str) -> int:
        if not db_id.startswith("db"):
            raise ValueError(f"Expected DB ID to start with 'db'")

        db_id = int(db_id[2:])

        if db_id < 0 or db_id > 15:
            raise ValueError(f"DB ID is out of range")

        return db_id

    async def scan_table(self, *, table: RedisTableIdentifier, columns: typing.AbstractSet[str]) -> typing.AsyncGenerator[DataFrame, None]:
        if table.table == RedisTableNames.KEYS:
            cursor = 0
            conn = await self._connections.get_connection(db_identifier=table.db_identifier)

            while True:
                cursor, keys = await conn.scan(cursor=cursor, match="*", count=self._config.scan_chunk_size)

                if keys:
                    records = []

                    for key in keys:
                        # TODO - add more columns
                        record = {StatQLInternalColumns.ROW_ID: key}

                        if RedisKeysTableColumns.KEY in columns:
                            record[RedisKeysTableColumns.KEY] = key

                        records.append(record)

                    yield DataFrame(records)

                if cursor == 0:
                    break

        else:
            raise NotImplementedError

    async def estimate_row_count(self, *, table: RedisTableIdentifier) -> int:
        if table.table == RedisTableNames.KEYS:
            conn = await self._connections.get_connection(db_identifier=table.db_identifier)
            num_keys = await conn.dbsize()
            return num_keys

        else:
            raise NotImplementedError

    async def fetch_all_tables(self, *, integration_config: RedisIntegrationConfig) -> typing.AsyncGenerator[TableInfo, None]:
        conn = await self._connections.get_connection(db_identifier=RedisDatabaseIdentifier(cluster_name=integration_config.cluster_name, db=0))
        num_databases = await RedisClient.get_db_count(conn=conn)

        for db_id in range(num_databases):
            yield TableInfo(
                path=(integration_config.cluster_name, str(db_id), RedisTableNames.KEYS),
                columns={RedisKeysTableColumns.KEY},
            )

    async def close(self) -> None:
        await self._connections.close()
