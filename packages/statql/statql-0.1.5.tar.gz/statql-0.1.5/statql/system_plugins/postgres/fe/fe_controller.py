import typing

import streamlit as st

from statql.common import IFEController, IntegrationInfo, SecretsManager
from ..common import PostgresIntegrationConfig


# todo: move config to common


class PostgresFEController(IFEController):
    title = "🐘 PostgresSQL"

    @classmethod
    def get_integration_form(cls) -> typing.Dict:
        return {
            "cluster_name": st.text_input("Cluster name (an alias that will be used in queries)", max_chars=20),
            "host": st.text_input("Host"),
            "port": st.text_input("Port"),
            "username": st.text_input("Username"),
            "password": st.text_input("Password", type="password"),
        }

    @classmethod
    def build_integration_config(cls, *, integration_form_input: typing.Mapping[str, typing.Any]) -> PostgresIntegrationConfig:
        cluster_name = integration_form_input["cluster_name"].lower()
        secret_name = SecretsManager.store_secret(secret_name_prefix=f"postgres-password-{cluster_name}", secret_value=integration_form_input["password"])

        return PostgresIntegrationConfig(
            cluster_name=cluster_name,
            host=integration_form_input["host"].lower(),
            port=integration_form_input["port"],
            user=integration_form_input["username"],
            password_secret_name=secret_name,
        )

    @classmethod
    def verify_integration_not_exists(
        cls, *, new_integration: PostgresIntegrationConfig, existing_integrations: typing.Iterable[PostgresIntegrationConfig]
    ) -> str | None:
        if new_integration.host in {integration.host for integration in existing_integrations}:
            return "Host is already integrated"

        if new_integration.cluster_name in {integration.cluster_name for integration in existing_integrations}:
            return "Cluster name is already used"

    @classmethod
    def get_integration_info(cls, *, config: PostgresIntegrationConfig) -> IntegrationInfo:
        return IntegrationInfo(
            name=config.cluster_name,
            details=[
                ("Host", config.host),
                ("Port", str(config.port)),
                ("Username", config.user),
            ],
        )
