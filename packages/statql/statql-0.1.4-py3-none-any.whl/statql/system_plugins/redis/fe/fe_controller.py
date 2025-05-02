import typing

import streamlit as st

from statql.common import IFEController, IntegrationInfo
from ..common import RedisIntegrationConfig


class RedisFEController(IFEController[RedisIntegrationConfig]):
    title = "🟥 Redis"

    @classmethod
    def get_integration_form(cls) -> typing.Dict[str, typing.Any]:
        return {
            "cluster_name": st.text_input("Cluster name (an alias that will be used in queries)", max_chars=20),
            "host": st.text_input("Host"),
            "port": st.text_input("Port"),
            "username": st.text_input("Username"),
            "password": st.text_input("Password", type="password"),
        }

    @classmethod
    def build_integration_config(cls, *, integration_form_input: typing.Mapping[str, typing.Any]) -> RedisIntegrationConfig:
        return RedisIntegrationConfig(
            cluster_name=integration_form_input["cluster_name"],
            host=integration_form_input["host"],
            port=int(integration_form_input["port"]),
            username=integration_form_input["username"],
            password=integration_form_input["password"],
        )

    @classmethod
    def verify_integration_not_exists(
        cls, *, new_integration: RedisIntegrationConfig, existing_integrations: typing.Iterable[RedisIntegrationConfig]
    ) -> str | None:
        if new_integration.host in {integration.host for integration in existing_integrations}:
            return "Host is already integrated"

        if new_integration.cluster_name in {integration.cluster_name for integration in existing_integrations}:
            return "Cluster name is already used"

    @classmethod
    def get_integration_info(cls, *, config: RedisIntegrationConfig) -> IntegrationInfo:
        details = [
            ("Host", config.host),
            ("Port", str(config.port)),
        ]

        if config.username is not None:
            details.append(("Username", config.username))

        return IntegrationInfo(name=config.cluster_name, details=details)
