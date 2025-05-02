import typing
from asyncio import Lock
from collections import defaultdict
from logging import getLogger

import psycopg

from .common import DatabaseIdentifier
from ..common import PostgresIntegrationConfig

logger = getLogger(__name__)


class PostgresConnectionsManager:
    def __init__(self, *, integrations: typing.Iterable[PostgresIntegrationConfig]):
        self._cluster_name_to_config = {integration.cluster_name: integration for integration in integrations}
        self._connections: typing.Dict[DatabaseIdentifier, psycopg.AsyncConnection] = {}
        self._locks: typing.Dict[DatabaseIdentifier, Lock] = defaultdict(Lock)  # todo: possibly lock for locks

    async def get_connection(self, *, db_identifier: DatabaseIdentifier) -> psycopg.AsyncConnection:
        try:
            return self._connections[db_identifier]
        except KeyError:
            async with self._locks[db_identifier]:
                if not (conn := self._connections.get(db_identifier)):  # Double check after lock acquired
                    dsn = self._build_dsn(db_identifier=db_identifier)
                    logger.debug(f"Connecting to {db_identifier}")
                    conn = await psycopg.AsyncConnection.connect(dsn, connect_timeout=5)
                    await conn.set_autocommit(True)
                    self._connections[db_identifier] = conn

                return conn

    def _build_dsn(self, *, db_identifier: DatabaseIdentifier) -> str:
        config = self._cluster_name_to_config[db_identifier.cluster_name]
        return f"postgresql://{config.user}:{config.password}@{config.host}:{config.port}/{db_identifier.db_name}"

    async def close(self) -> None:
        for db_identifier, connection in self._connections.items():
            async with self._locks[db_identifier]:
                await connection.close()
