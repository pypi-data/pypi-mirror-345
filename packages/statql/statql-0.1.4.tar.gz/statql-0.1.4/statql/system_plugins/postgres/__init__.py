from statql.common import PluginBlueprint
from .catalog import PostgresCatalog
from .common import PostgresCatalogConfig, PostgresIntegrationConfig
from .fe import PostgresFEController

POSTGRES_BLUEPRINT = PluginBlueprint(
    catalog_name="pg",
    fe_controller_cls=PostgresFEController,
    integration_config_cls=PostgresIntegrationConfig,
    catalog_config_cls=PostgresCatalogConfig,
    catalog_cls=PostgresCatalog,
)
