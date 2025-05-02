import typing

from pandas import DataFrame, Series

from statql.common import timer
from ..common import (
    IPlanNode,
    StatQLContext,
    Term,
    BooleanExpression,
    BinaryBooleanExpression,
    BooleanBinaryOperators,
    get_term_column_name,
    Constant,
    validate_columns,
    PopulationPipelineBatch,
)


class Filter(IPlanNode):
    def __init__(self, *, input: IPlanNode[PopulationPipelineBatch], condition: BooleanExpression):
        super().__init__()
        self._input = input
        self._condition = condition

    def get_output_terms(self) -> typing.Set[Term]:
        return self._input.get_output_terms()

    def execute(self, *, ctx: StatQLContext) -> typing.Generator[PopulationPipelineBatch, None, None]:
        for batch in self._input.execute(ctx=ctx):
            validate_columns(df=batch.data, expected_terms=self._input.get_output_terms())

            with timer(name="Filtering"):
                filter_series = self._build_filter_series(df=batch.data, bool_exp=self._condition)
                new_data = batch.data[filter_series]

                batch.table_estimated_size = int(len(new_data) / len(batch.data) * batch.table_estimated_size)
                batch.data = new_data

            yield batch

    @classmethod
    def _build_filter_series(cls, *, df: DataFrame, bool_exp: BooleanExpression) -> Series:
        if isinstance(bool_exp, BinaryBooleanExpression):
            if isinstance(bool_exp.left, Constant):
                left = Series([bool_exp.left.value] * len(df))
            elif isinstance(bool_exp.left, Term):
                left = df[get_term_column_name(bool_exp.left)]
            else:
                left = cls._build_filter_series(df=df, bool_exp=bool_exp.left)

            if isinstance(bool_exp.right, Constant):
                right = Series([bool_exp.right.value] * len(df))
            elif isinstance(bool_exp.right, Term):
                right = df[get_term_column_name(bool_exp.right)]
            else:
                right = cls._build_filter_series(df=df, bool_exp=bool_exp.right)

            if bool_exp.operator == BooleanBinaryOperators.EQ:
                return left == right
            elif bool_exp.operator == BooleanBinaryOperators.NEQ:
                return left != right
            elif bool_exp.operator == BooleanBinaryOperators.GT:
                return left > right
            elif bool_exp.operator == BooleanBinaryOperators.LT:
                return left < right
            elif bool_exp.operator == BooleanBinaryOperators.AND:
                return left and right
            elif bool_exp.operator == BooleanBinaryOperators.OR:
                return left or right
            else:
                raise NotImplementedError

        else:
            raise NotImplementedError
