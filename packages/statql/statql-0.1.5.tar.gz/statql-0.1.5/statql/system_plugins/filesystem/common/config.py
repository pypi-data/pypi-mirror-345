from statql.common import Model


class FileSystemIntegrationConfig(Model):
    file_system_name: str
    root_path: str


class FileSystemCatalogConfig(Model):
    scan_chunk_size: int = 10_000
