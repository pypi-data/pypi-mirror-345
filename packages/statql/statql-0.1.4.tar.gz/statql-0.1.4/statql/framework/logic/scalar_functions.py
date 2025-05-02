import abc
import typing

from pandas import Series

from ..common import ScalarFunctionNames


class IScalarFunction(abc.ABC):
    name: typing.ClassVar[ScalarFunctionNames]
    num_args: typing.ClassVar[int]

    def __init_subclass__(cls, **kwargs):
        _ = cls.num_args  # Validating existence
        SCALAR_FUNCTION_NAME_TO_CLS[cls.name] = cls
        super().__init_subclass__(**kwargs)

    @classmethod
    def execute(cls, *arguments: Series) -> Series:
        raise NotImplementedError


SCALAR_FUNCTION_NAME_TO_CLS: typing.Dict[ScalarFunctionNames, typing.Type[IScalarFunction]] = {}


def get_scalar_function_cls(*, func_name: ScalarFunctionNames) -> typing.Type[IScalarFunction]:
    return SCALAR_FUNCTION_NAME_TO_CLS[func_name]


class Identity(IScalarFunction):
    name = ScalarFunctionNames.IDENTITY
    num_args = 1

    @classmethod
    def execute(cls, arg: Series) -> Series:
        return arg


class GetFileExt(IScalarFunction):
    name = ScalarFunctionNames.GET_FILE_EXT
    num_args = 1

    @classmethod
    def execute(cls, arg: Series) -> Series:
        return arg.str.extract(r"\.([^.\\/]+)$", expand=False)


class Concat(IScalarFunction):
    name = ScalarFunctionNames.CONCAT
    num_args = 2

    @classmethod
    def execute(cls, a: Series, b: Series | str) -> Series:
        return a + b


class Divide(IScalarFunction):
    name = ScalarFunctionNames.DIVIDE
    num_args = 2

    @classmethod
    def execute(cls, column: Series, divide_by: Series | int | float) -> Series:
        return column / divide_by


class Split(IScalarFunction):
    name = ScalarFunctionNames.SPLIT
    num_args = 2

    @classmethod
    def execute(cls, column: Series, split_by: str) -> Series:
        return column.str.split(split_by, regex=False)


class GetItem(IScalarFunction):
    name = ScalarFunctionNames.GET_ITEM
    num_args = 2

    @classmethod
    def execute(cls, column: Series, key: int | typing.Hashable) -> Series:
        return column.str[key]
