from statql.common import PluginBlueprint
from .catalog import RedisCatalog
from .common import RedisCatalogConfig, RedisIntegrationConfig
from .fe import RedisFEController

REDIS_BLUEPRINT = PluginBlueprint(
    catalog_name="redis",
    fe_controller_cls=RedisFEController,
    catalog_cls=RedisCatalog,
    catalog_config_cls=RedisCatalogConfig,
    integration_config_cls=RedisIntegrationConfig,
)
