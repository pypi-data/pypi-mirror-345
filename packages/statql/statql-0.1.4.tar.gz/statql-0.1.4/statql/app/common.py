from __future__ import annotations

import json
import logging
import os
import typing
from concurrent.futures import ThreadPoolExecutor

from platformdirs import user_data_dir
from pydantic import ConfigDict

from statql.common import Model
from statql.framework import StatQLConfig, StatQLClient

logger = logging.getLogger(__name__)

STATQL_APP_DATA_PATH = os.environ.get("STATQL_APP_DATA_PATH", user_data_dir("StatQL", appauthor="liel"))
os.makedirs(STATQL_APP_DATA_PATH, exist_ok=True)


class GlobalState(Model):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    completions_manager: CompletionsManager


class ConfigManager:
    _CONFIG_PATH = os.path.join(STATQL_APP_DATA_PATH, "config.json")

    @classmethod
    def get_config(cls) -> StatQLConfig:
        logger.info(f"Loading config from {cls._CONFIG_PATH}...")

        try:
            with open(cls._CONFIG_PATH, "r") as f:
                return StatQLConfig(**json.load(f))
        except FileNotFoundError:
            return StatQLConfig(
                integrations={},
                catalog_name_to_config={},  # todo: ?
                cache_dir_path=os.path.join(STATQL_APP_DATA_PATH, "cache"),
            )

    @classmethod
    def save_config(cls, *, config: StatQLConfig) -> None:
        logger.info(f"Saving config to {cls._CONFIG_PATH}")

        with open(cls._CONFIG_PATH, "w") as f:
            json.dump(config.model_dump(mode="json"), f, indent=3)


class CompletionsManager:
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="introspector")
        self._completions = {}

    def request(self, integration_ids: typing.Iterable[str]):
        for integration_id in integration_ids:
            self._executor.submit(self._populate_completions_for_integration, integration_id=integration_id)

    def _populate_completions_for_integration(self, *, integration_id: str) -> None:
        try:
            logger.info(f"Fetching completions...")

            config = ConfigManager.get_config()

            with StatQLClient(config=config) as client:
                for table_info in client.fetch_all_tables(integration_id=integration_id):
                    full_table_path = ".".join(table_info.path)

                    # Table completion
                    self._completions[full_table_path] = {
                        "caption": full_table_path,
                        "value": full_table_path,
                        "meta": "table",
                        "name": full_table_path,
                        "sframework": 1,
                    }

                    for column_name in table_info.columns:
                        self._completions[f"{full_table_path}:{column_name}"] = {
                            "caption": f"{table_info.path[-1]}.{column_name}",
                            "value": column_name,
                            "meta": "column",
                            "name": f"{full_table_path}:{column_name}",
                            "sframework": 1,
                        }

        except Exception as e:
            # TODO: sometimes this doesnt print?
            logger.exception(f"Failed to populate completions for integration {integration_id}: {e}")

    def get_all_completions(self) -> typing.List[typing.Dict]:
        return list(self._completions.values())
