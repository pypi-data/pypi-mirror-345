import typing

from pydantic import SerializeAsAny

from statql.common import Model
from statql.framework.client.plugins_manager import PluginsManager  # TODO: fix this


class StatQLIntegration(Model):
    catalog_name: str
    config: SerializeAsAny[Model]

    @classmethod
    def transform(cls, obj: typing.MutableMapping) -> None:
        config = obj["config"]

        if isinstance(config, Model):
            pass  # Nothing to do

        elif isinstance(config, typing.Mapping):
            plugin = PluginsManager.get_plugin_by_catalog_name(catalog_name=obj["catalog_name"])
            obj["config"] = plugin.integration_config_cls(**config)

        else:
            raise TypeError(f"Unexpected config type: {type(config).__name__}")


class StatQLConfig(Model):
    cache_dir_path: str
    integrations: typing.MutableMapping[str, StatQLIntegration]
    catalog_name_to_config: typing.MutableMapping[str, SerializeAsAny[Model]]
