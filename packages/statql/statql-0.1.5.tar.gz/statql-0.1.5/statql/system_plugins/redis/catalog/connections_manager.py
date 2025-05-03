import typing
from asyncio import Lock
from collections import defaultdict
from logging import getLogger

from redis.asyncio import Redis

from statql.common import SecretsManager
from .common import RedisDatabaseIdentifier
from ..common import RedisIntegrationConfig

logger = getLogger(__name__)


class RedisConnectionsManager:
    def __init__(self, *, integrations: typing.Iterable[RedisIntegrationConfig]):
        self._cluster_name_to_config = {integration.cluster_name: integration for integration in integrations}
        self._connections: typing.Dict[RedisDatabaseIdentifier, Redis] = {}
        self._locks: typing.Dict[RedisDatabaseIdentifier, Lock] = defaultdict(Lock)  # todo: possibly lock for locks

    async def get_connection(self, *, db_identifier: RedisDatabaseIdentifier) -> Redis:
        try:
            return self._connections[db_identifier]
        except KeyError:
            async with self._locks[db_identifier]:
                if not (redis := self._connections.get(db_identifier)):  # Double check after lock acquired
                    logger.debug(f"Connecting to {db_identifier}")
                    cluster_config = self._cluster_name_to_config[db_identifier.cluster_name]

                    if cluster_config.password_secret_name is not None:
                        password = SecretsManager.get_secret(secret_name=cluster_config.password_secret_name)
                    else:
                        password = None

                    redis = Redis(
                        host=cluster_config.host,
                        port=cluster_config.port,
                        username=cluster_config.username,
                        password=password,
                        decode_responses=True,
                    )
                    self._connections[db_identifier] = redis

                return redis

    async def close(self) -> None:
        for db_identifier, redis in self._connections.items():
            async with self._locks[db_identifier]:
                await redis.close()
