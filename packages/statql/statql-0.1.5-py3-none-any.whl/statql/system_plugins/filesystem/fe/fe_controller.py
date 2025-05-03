import typing

import streamlit as st

from statql.common import IFEController, IntegrationInfo
from ..common import FileSystemIntegrationConfig


# TODO - handle non-case-sensitive file systems and case-sensitive file systems separately


class FileSystemFEController(IFEController[FileSystemIntegrationConfig]):
    title = "📁 File System"

    @classmethod
    def get_integration_form(cls) -> typing.Dict[str, typing.Any]:
        return {"fs_name": st.text_input("File system name (an alias that will be usd in queries)", max_chars=20), "root_path": st.text_input("Root path")}

    @classmethod
    def build_integration_config(cls, *, integration_form_input: typing.Mapping[str, typing.Any]) -> FileSystemIntegrationConfig:
        return FileSystemIntegrationConfig(file_system_name=integration_form_input["fs_name"].lower(), root_path=integration_form_input["root_path"])

    @classmethod
    def verify_integration_not_exists(
        cls, *, new_integration: FileSystemIntegrationConfig, existing_integrations: typing.Iterable[FileSystemIntegrationConfig]
    ) -> str | None:
        if new_integration.root_path in {integration.root_path for integration in existing_integrations}:
            return "File system is already integrated"

        if new_integration.file_system_name in {integration.file_system_name for integration in existing_integrations}:
            return "File system name is already used"

    @classmethod
    def get_integration_info(cls, *, config: FileSystemIntegrationConfig) -> IntegrationInfo:
        return IntegrationInfo(
            name=config.file_system_name,
            details=[
                ("Root path", config.root_path),
            ],
        )
