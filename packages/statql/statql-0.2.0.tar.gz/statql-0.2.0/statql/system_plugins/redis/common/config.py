from statql.common import Model


class RedisIntegrationConfig(Model):
    cluster_name: str
    host: str
    port: int
    username: str | None = None
    password_secret_name: str | None = None


class RedisCatalogConfig(Model):
    scan_chunk_size: int = 10_000
