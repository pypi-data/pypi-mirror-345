from __future__ import annotations

import typing
from logging import getLogger

from statql.common import timer
from .reservoir import Reservoir
from ..common import IPlanNode, StatQLContext, Term, AggregationPipelineBatch, validate_columns

logger = getLogger(__name__)


class SampleReservoir(IPlanNode[AggregationPipelineBatch]):
    def __init__(self, *, reservoir: Reservoir):
        super().__init__()
        self._reservoir = reservoir

    def get_output_terms(self) -> typing.Set[Term]:
        return self._reservoir.terms

    def execute(self, *, ctx: StatQLContext) -> typing.Generator[AggregationPipelineBatch, None, None]:
        while True:
            with timer(name="Fetch sample"):
                data, total_size = self._reservoir.build_sample()
                validate_columns(df=data, expected_terms=self._reservoir.terms)

            yield AggregationPipelineBatch(data=data, population_estimated_size=total_size)
