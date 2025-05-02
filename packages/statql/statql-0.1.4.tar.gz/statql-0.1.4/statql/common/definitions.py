import abc
import enum
import typing

from pandas import DataFrame

from .cache import CacheManager
from .utils import FrozenModel, Model

TableIdentifier = typing.Hashable


class StatQLInternalColumns(enum.StrEnum):
    ROW_ID = "__statql_row_id__"


class TableInfo(FrozenModel):
    path: typing.Sequence[str]
    columns: typing.AbstractSet[str]


class ICatalog[ConfigT: Model, IntegrationConfigT: Model, TableIdentifierT: TableIdentifier](abc.ABC):
    def __init__(self, *, cache_manager: CacheManager, config: ConfigT, integrations: typing.Iterable[IntegrationConfigT]):
        self._config = config
        self._integrations = integrations
        self._cache = cache_manager

    @abc.abstractmethod
    def resolve_table_path(self, *, table_path: typing.Sequence[str]) -> typing.Generator[TableIdentifierT, None, None]:
        raise NotImplementedError

    @abc.abstractmethod
    def scan_table(self, *, table: TableIdentifierT, columns: typing.AbstractSet[str]) -> typing.Generator[DataFrame, None, None]:
        raise NotImplementedError

    @abc.abstractmethod
    def estimate_row_count(self, *, table: TableIdentifierT) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_all_tables(self, *, integration_config: IntegrationConfigT) -> typing.Generator[TableInfo, None, None]:
        raise NotImplementedError

    @abc.abstractmethod
    def close(self) -> None:
        raise NotImplementedError


class IAsyncCatalog[ConfigT: Model, IntegrationConfigT: Model, TableIdentifierT: typing.Hashable](abc.ABC):
    def __init__(self, *, cache_manager: CacheManager, config: ConfigT, integrations: typing.Iterable[IntegrationConfigT]):
        self._config = config
        self._integrations = integrations
        self._cache = cache_manager

    @abc.abstractmethod
    async def resolve_table_path(self, *, table_path: typing.Sequence[str]) -> typing.AsyncGenerator[TableIdentifierT, None]:
        raise NotImplementedError

    @abc.abstractmethod
    async def scan_table(self, *, table: TableIdentifierT, columns: typing.AbstractSet[str]) -> typing.AsyncGenerator[DataFrame, None]:
        raise NotImplementedError

    @abc.abstractmethod
    async def estimate_row_count(self, *, table: TableIdentifierT) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    async def fetch_all_tables(self, *, integration_config: IntegrationConfigT) -> typing.AsyncGenerator[TableInfo, None]:
        raise NotImplementedError

    @abc.abstractmethod
    async def close(self) -> None:
        raise NotImplementedError


class IntegrationInfo(FrozenModel):
    name: str
    details: typing.Sequence[typing.Tuple[str, str]]


class IFEController[IntegrationConfigT: Model](abc.ABC):
    title: typing.ClassVar[str]

    def __init_subclass__(cls, **kwargs):
        # Making sure everything is set
        _ = cls.title

        super().__init_subclass__(**kwargs)

    @classmethod
    @abc.abstractmethod
    def get_integration_form(cls) -> typing.Dict[str, typing.Any]:
        raise NotImplementedError  # Use streamlit inputs to get user inputs. Return user inputs (eg {"name": "liel"})

    @classmethod
    @abc.abstractmethod
    def build_integration_config(cls, *, integration_form_input: typing.Mapping[str, typing.Any]) -> IntegrationConfigT:
        raise NotImplementedError  # Builds integration config from user input

    @classmethod
    @abc.abstractmethod
    def verify_integration_not_exists(cls, *, new_integration: IntegrationConfigT, existing_integrations: typing.Iterable[IntegrationConfigT]) -> str | None:
        raise NotImplementedError  # Returns an error message in case some detail in new_integration is colliding with existing_integrations

    @classmethod
    @abc.abstractmethod
    def get_integration_info(cls, *, config: IntegrationConfigT) -> IntegrationInfo:
        raise NotImplementedError  # Returns integration details to display when clicking on existing integration (key value, no sensitive info)


class PluginBlueprint(FrozenModel):
    catalog_name: str
    fe_controller_cls: typing.Type[IFEController]
    catalog_cls: typing.Type[ICatalog | IAsyncCatalog]
    catalog_config_cls: typing.Type[Model]
    integration_config_cls: typing.Type[Model]
