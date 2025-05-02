import enum

from statql.common import FrozenModel


class RedisTableNames(enum.StrEnum):
    KEYS = "keys"


class RedisKeysTableColumns(enum.StrEnum):
    KEY = "key"
    VALUE = "value"


class RedisDatabaseIdentifier(FrozenModel):
    cluster_name: str
    db: int


class RedisTableIdentifier(FrozenModel):
    cluster_name: str
    db: int
    table: RedisTableNames

    @property
    def db_identifier(self) -> RedisDatabaseIdentifier:
        return RedisDatabaseIdentifier(cluster_name=self.cluster_name, db=self.db)
