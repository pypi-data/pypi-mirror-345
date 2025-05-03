import typing

from statql.common import timer
from ..common import IPlanNode, StatQLContext, Term, get_term_column_name, Batch, AggregationFunction, validate_columns


class Materialize(IPlanNode):
    def __init__(self, *, input: IPlanNode, term_to_alias: typing.Mapping[Term, str | None]):
        super().__init__()
        self._input = input
        self._term_to_alias = term_to_alias

    def get_output_terms(self) -> typing.Set[Term]:
        return set(self._term_to_alias)

    def execute(self, *, ctx: StatQLContext) -> typing.Generator[Batch, None, None]:
        rename_map = {get_term_column_name(term): alias for term, alias in self._term_to_alias.items() if alias is not None}

        input_terms = self._input.get_output_terms()
        output_terms = self.get_output_terms()

        # Removing un-queried terms
        column_names_to_drop = {get_term_column_name(term) for term in input_terms - output_terms}

        # Aggregation terms result in Estimation objects, which is a custom type. To prevent compatibility issues with streamlit component, we convert to string
        column_names_to_convert_to_str = {get_term_column_name(term) for term in input_terms if isinstance(term, AggregationFunction)}

        for batch in self._input.execute(ctx=ctx):
            validate_columns(df=batch.data, expected_terms=self._input.get_output_terms())

            with timer(name="Materialize"):
                for col in column_names_to_convert_to_str:
                    batch.data[col] = batch.data[col].astype(str)

                for col in column_names_to_drop:
                    del batch.data[col]

                batch.data.rename(columns=rename_map, inplace=True)

            yield batch
