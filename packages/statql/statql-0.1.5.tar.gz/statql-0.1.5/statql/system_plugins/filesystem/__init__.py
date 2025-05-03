from statql.common import PluginBlueprint
from .catalog import FileSystemCatalog
from .common import FileSystemIntegrationConfig, FileSystemCatalogConfig
from .fe import FileSystemFEController

FILE_SYSTEM_BLUEPRINT = PluginBlueprint(
    catalog_name="fs",
    fe_controller_cls=FileSystemFEController,
    integration_config_cls=FileSystemIntegrationConfig,
    catalog_config_cls=FileSystemCatalogConfig,
    catalog_cls=FileSystemCatalog,
)
