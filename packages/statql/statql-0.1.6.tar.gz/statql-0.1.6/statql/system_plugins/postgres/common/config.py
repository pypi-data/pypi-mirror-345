from pydantic import Field

from statql.common import SamplingConfig, Model


class PostgresIntegrationConfig(Model):
    cluster_name: str = Field(frozen=True)
    host: str
    port: int
    user: str
    password_secret_name: str

    def get_unique_id(self) -> str:
        return self.cluster_name


class PostgresCatalogConfig(Model):
    scan_chunk_size: int = 10_000
    sampling_config: SamplingConfig = SamplingConfig()
