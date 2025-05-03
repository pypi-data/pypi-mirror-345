import random
import typing

import numpy as np
from pandas import DataFrame, concat

from statql.common import StatQLInternalColumns, scale_sequence, TableIdentifier
from ..common import Term, get_term_column_name, Estimation, PopulationPipelineBatch, AggregationPipelineBatch


class Reservoir:
    def __init__(self, *, table_reservoir_max_size: int, terms: typing.AbstractSet[Term]):
        self._table_reservoir_max_size = table_reservoir_max_size
        self._tables: typing.Dict[TableIdentifier, typing.Tuple[_TableDataReservoir, _PopulationSizeEstimationsReservoir, int]] = {}
        self._terms = terms

    def ingest_population_pipeline_batch(self, *, batch: PopulationPipelineBatch) -> None:
        if batch.original_batch_size == 0:
            return  # We don't care about empty batches

        if batch.table in self._tables:
            data_reservoir, ratios_reservoir, table_size = self._tables[batch.table]
        else:
            data_reservoir = _TableDataReservoir(reservoir_max_size=self._table_reservoir_max_size)
            ratios_reservoir = _PopulationSizeEstimationsReservoir(reservoir_max_size=1000)  # TODO: configurable
            self._tables[batch.table] = data_reservoir, ratios_reservoir, batch.table_size

        data_reservoir.ingest_data(data=batch.data)
        ratios_reservoir.ingest_population_ratio_observation(population_ratio=len(batch.data) / batch.original_batch_size)

    def build_aggregation_pipeline_batch(self) -> AggregationPipelineBatch:
        # Returns sample and estimated total size of all tables
        table_identifier_to_population_size_estimation = {}

        for table, (_, population_ratios_reservoir, table_size) in list(self._tables.items()):
            table_identifier_to_population_size_estimation[table] = population_ratios_reservoir.estimate_population_ratio() * table_size

        total_population_estimated_size = Estimation.sum_independent_ests(table_identifier_to_population_size_estimation.values())
        samples: typing.List[DataFrame] = []

        for table, size_est in table_identifier_to_population_size_estimation.items():
            table_size_ratio = size_est.value / total_population_estimated_size.value

            data_reservoir, _, _ = self._tables[table]

            table_sample = data_reservoir.sample(sample_size=max(int(table_size_ratio * self._table_reservoir_max_size), 1))
            samples.append(table_sample)

        if samples:
            return AggregationPipelineBatch(
                data=concat(samples, ignore_index=True),
                population_estimated_size=total_population_estimated_size,
            )
        else:
            return AggregationPipelineBatch(
                data=DataFrame(columns=[get_term_column_name(term) for term in self._terms]),
                population_estimated_size=total_population_estimated_size,
            )

    @property
    def terms(self) -> typing.Set[Term]:
        return set(self._terms)


class _TableDataReservoir:
    def __init__(self, *, reservoir_max_size: int):
        self._reservoir_max_size = reservoir_max_size
        self._canonical_columns: typing.List[str] | None = None
        self._visited_row_count = 0
        self._row_ids_in_reservoir = set()
        self._table_data_reservoir: typing.List[typing.Tuple] = []

    def ingest_data(self, *, data: DataFrame) -> None:
        # We are sorting columns by name because we rely on consistent column order later on
        if not self._canonical_columns:
            self._canonical_columns = sorted(data.columns)

        data = data[self._canonical_columns]

        row_id_index = self._canonical_columns.index(StatQLInternalColumns.ROW_ID)

        for row in data.itertuples(index=False):
            self._visited_row_count += 1

            row_id = row[row_id_index]

            if row_id in self._row_ids_in_reservoir:
                continue

            if len(self._table_data_reservoir) < self._reservoir_max_size:
                self._table_data_reservoir.append(row)
                self._row_ids_in_reservoir.add(row_id)
            else:
                index = random.randint(0, self._visited_row_count)

                if index < self._reservoir_max_size:
                    reservoir_row_id_to_replace = self._table_data_reservoir[index][row_id_index]
                    self._row_ids_in_reservoir.remove(reservoir_row_id_to_replace)
                    self._row_ids_in_reservoir.add(row_id)
                    self._table_data_reservoir[index] = row

    def sample(self, *, sample_size: int) -> DataFrame:
        if sample_size < 1:
            raise ValueError

        # If the reservoir is smaller than its max size, we scale it artificially by replicating elements.
        if len(self._table_data_reservoir) < self._reservoir_max_size:
            scale_factor = self._reservoir_max_size / len(self._table_data_reservoir)
            reservoir = scale_sequence(seq=self._table_data_reservoir, factor=scale_factor)
        else:
            reservoir = self._table_data_reservoir

        sample = random.sample(reservoir, sample_size)

        df = DataFrame(sample)
        df.columns = self._canonical_columns
        df.drop(StatQLInternalColumns.ROW_ID, axis=1, inplace=True)

        return df


class _PopulationSizeEstimationsReservoir:
    def __init__(self, *, reservoir_max_size: int):
        self._reservoir_max_size = reservoir_max_size
        self._ratios_count = 0
        self._population_ratios_reservoir: typing.List[float] = []

    def ingest_population_ratio_observation(self, *, population_ratio: float) -> None:
        if self._ratios_count < self._reservoir_max_size:
            self._population_ratios_reservoir.append(population_ratio)
        else:
            index = random.randint(0, self._ratios_count)

            if index < self._reservoir_max_size:
                self._population_ratios_reservoir[index] = population_ratio

    def estimate_population_ratio(self, *, alpha: float = 0.05, bootstrap_iterations: int = 1000) -> Estimation:
        data = np.array(self._population_ratios_reservoir)
        n = data.shape[0]

        samples = np.random.choice(data, size=(bootstrap_iterations, n), replace=True)

        means = samples.mean(axis=1)

        lower, upper = np.percentile(means, [100 * (alpha / 2), 100 * (1 - alpha / 2)])

        point_estimation = data.mean()

        return Estimation(point_estimation, (upper - lower) / 2)
