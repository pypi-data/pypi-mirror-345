from __future__ import annotations

import typing
from dataclasses import dataclass

from statql.common import invert_map
from .quey_parser import ParsedQuery
from ..common import (
    IPlanNode,
    Term,
    TableColumn,
    AggregationFunction,
    ScalarFunction,
    PopulationPipelineBatch,
    AggregationPipelineBatch,
)
from ..logic import Aggregate, Filter, Limit, Materialize, Order, Project, SampleReservoir, Scan, Reservoir, UpdateReservoir


@dataclass
class ExecutionPlan:
    population_plan: IPlanNode[PopulationPipelineBatch]
    aggregation_plan: IPlanNode[AggregationPipelineBatch]


class Planner:
    @classmethod
    def plan(cls, *, parsed_query: ParsedQuery) -> ExecutionPlan:
        all_terms = cls._get_all_terms(parsed_query=parsed_query)

        # ------------- Population Plan -------------
        population_plan = Scan(
            catalog_name=parsed_query.from_.catalog_name,
            table_path=parsed_query.from_.table_path,
            columns={term for term in all_terms if isinstance(term, TableColumn)},
        )

        if parsed_query.where:
            scalar_funcs_introduced_in_where = {term for term in parsed_query.where.get_args_recursive() if isinstance(term, ScalarFunction)}

            # If WHERE statement uses scalar function, need to add a projection so that this scalar function will be defined
            if scalar_funcs_introduced_in_where:
                population_plan = Project(input=population_plan, new_terms=scalar_funcs_introduced_in_where)

            population_plan = Filter(input=population_plan, condition=parsed_query.where)

        # The reservoir is the thing that connects the population plan and the aggregation plan.
        # Population plan is for populating the reservoir, and aggregation plan is for calculating results based on the reservoir.
        reservoir = Reservoir(table_reservoir_max_size=10_000, terms=population_plan.get_output_terms())  # TODO: configurable
        population_plan = UpdateReservoir(input=population_plan, reservoir=reservoir)

        # ------------- Aggregation Plan -------------
        aggregation_plan = SampleReservoir(reservoir=reservoir)

        aggregation_func_terms = {term for term in all_terms if isinstance(term, AggregationFunction)}

        if not aggregation_func_terms:
            raise SyntaxError("Only aggregation queries are supported (use an aggregation function like COUNT)")

        scalar_funcs_introduced_in_aggregation_funcs = set()

        for agg_func_term in aggregation_func_terms:
            scalar_func_args = {term for term in agg_func_term.get_args_recursive() if isinstance(term, ScalarFunction)}
            new_scalar_func_args = scalar_func_args - aggregation_plan.get_output_terms()
            scalar_funcs_introduced_in_aggregation_funcs.update(new_scalar_func_args)

        scalar_funcs_introduced_in_group_bys = {
            term for term in parsed_query.group_bys if isinstance(term, ScalarFunction)
        } - aggregation_plan.get_output_terms()

        # If aggregation step relies on scalar function terms that are not available already, add a projection
        if scalar_funcs_introduced_in_group_bys or scalar_funcs_introduced_in_aggregation_funcs:
            aggregation_plan = Project(input=aggregation_plan, new_terms=scalar_funcs_introduced_in_aggregation_funcs | scalar_funcs_introduced_in_group_bys)

        # Make sure all group by terms are defined
        if unknown_group_bys := parsed_query.group_bys - aggregation_plan.get_output_terms():
            raise SyntaxError(f"Cannot group by unknown terms: {unknown_group_bys}")

        aggregation_plan = Aggregate(input=aggregation_plan, group_bys=parsed_query.group_bys, aggregations=aggregation_func_terms)

        if parsed_query.order_by:
            # If order by relies on scalar function terms that are not available already, add a projection
            if isinstance(parsed_query.order_by.term, ScalarFunction) and parsed_query.order_by.term not in aggregation_plan.get_output_terms():
                aggregation_plan = Project(input=aggregation_plan, new_terms={parsed_query.order_by.term})

            aggregation_plan = Order(input=aggregation_plan, term=parsed_query.order_by.term, desc=parsed_query.order_by.desc)

        if parsed_query.limit is not None:
            if parsed_query.limit < 1:
                raise SyntaxError("Limit must be greater than 0")

            aggregation_plan = Limit(input=aggregation_plan, limit=parsed_query.limit)

        # Check that all terms are either in the group by or are aggregation functions
        for final_term in parsed_query.alias_to_term.values():
            is_aggregation = isinstance(final_term, AggregationFunction) or any(isinstance(arg, AggregationFunction) for arg in final_term.get_args_recursive())

            if not is_aggregation and final_term not in parsed_query.group_bys:
                raise SyntaxError(f"Term is missing from group-by: {final_term}")

        aggregation_plan = Materialize(input=aggregation_plan, term_to_alias=invert_map(parsed_query.alias_to_term))

        return ExecutionPlan(population_plan=population_plan, aggregation_plan=aggregation_plan)

    @classmethod
    def _get_all_terms(cls, *, parsed_query: ParsedQuery) -> typing.Set[Term]:
        stack = []

        stack += list(parsed_query.alias_to_term.values())

        stack += parsed_query.group_bys

        if parsed_query.where:
            stack.append(parsed_query.where)

        all_terms = set()

        while stack:
            curr_term = stack.pop()
            all_terms.add(curr_term)
            stack += curr_term.get_args()

        return all_terms
