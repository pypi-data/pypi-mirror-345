import logging
import time
from uuid import uuid4

import streamlit as st
from pydantic import ValidationError

from common import ConfigManager, GlobalState
from statql.common import Model
from statql.framework import StatQLConfig, StatQLIntegration, PluginsManager

logger = logging.getLogger(__name__)


class IntegrationsState(Model):
    integrated_catalog_name: str | None = None


def main():
    global_state: GlobalState = st.session_state.global_state

    if "integrations_state" not in st.session_state:
        st.session_state.integrations_state = IntegrationsState()

    integrations_state = st.session_state.integrations_state

    config = ConfigManager.get_config()

    # New integrations button
    if st.button("New Integration", icon="➕", key="new_integration"):
        new_integration_dialog(config=config, global_state=global_state, integrations_state=integrations_state)

    for integration_id, integration in sorted(config.integrations.items(), key=lambda keyval: keyval[1].catalog_name):
        fe_controller = PluginsManager.get_plugin_by_catalog_name(catalog_name=integration.catalog_name).fe_controller_cls
        integration_info = fe_controller.get_integration_info(config=integration.config)

        with st.expander(f"{fe_controller.title} - {integration_info.name}"):
            for key, value in integration_info.details:
                st.write(f"{key}: {value}")

            if st.button("Delete", icon="🗑️", key=f"{integration_id}_delete"):
                delete_integration_dialog(config=config, integration_id=integration_id)


@st.dialog("Add Integration")
def new_integration_dialog(*, config: StatQLConfig, global_state: GlobalState, integrations_state: IntegrationsState) -> None:
    # Catalog selection
    st.write("What platform would you like to integrate?")

    cols = st.columns(2)

    for i, plugin in enumerate(PluginsManager.get_all()):
        with cols[i % 2]:
            if st.button(plugin.fe_controller_cls.title, use_container_width=True):
                integrations_state.integrated_catalog_name = plugin.catalog_name

    # Integration form of selected catalog
    if integrations_state.integrated_catalog_name:
        plugin = PluginsManager.get_plugin_by_catalog_name(catalog_name=integrations_state.integrated_catalog_name)
        fe_controller = plugin.fe_controller_cls

        with st.form("Integration Form"):
            user_input = fe_controller.get_integration_form()

            if st.form_submit_button("Add", icon="➕"):
                try:
                    integration_config = fe_controller.build_integration_config(integration_form_input=user_input)
                except ValidationError as e:
                    st.error(f"Invalid integration details: {e}")
                    return

                if collision_error := fe_controller.verify_integration_not_exists(
                    new_integration=integration_config,
                    existing_integrations=[
                        integration.config
                        for integration in config.integrations.values()
                        if integration.catalog_name == integrations_state.integrated_catalog_name
                    ],
                ):
                    st.error(collision_error)
                    return

                integration = StatQLIntegration(catalog_name=integrations_state.integrated_catalog_name, config=integration_config)
                integration_id = str(uuid4())

                config.integrations[integration_id] = integration
                ConfigManager.save_config(config=config)

                global_state.completions_manager.request(integration_ids=[integration_id])

                st.info("Successfully added integration!")

                time.sleep(1)
                st.rerun()


@st.dialog("Delete Integration")
def delete_integration_dialog(*, config: StatQLConfig, integration_id: str) -> None:
    st.markdown(f"Are you sure you want to delete this integration?")

    if st.button("Yes"):
        config.integrations.pop(integration_id)
        ConfigManager.save_config(config=config)

        st.info(f"Integration deleted")

        time.sleep(1)
        st.rerun()


if __name__ == "__main__":
    main()
