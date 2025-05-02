import random
import typing

import numpy as np
from pandas import DataFrame, concat

from statql.common import StatQLInternalColumns, scale_sequence, TableIdentifier
from ..common import Term, get_term_column_name, Estimation


class Reservoir:
    def __init__(self, *, table_reservoir_max_size: int, terms: typing.AbstractSet[Term]):
        self._table_reservoir_max_size = table_reservoir_max_size
        self._tables: typing.Dict[TableIdentifier, _TableReservoir] = {}
        self._terms = terms

    def ingest_data(self, *, table: TableIdentifier, data: DataFrame, table_estimated_size: int) -> None:
        reservoir = self._tables.get(table)

        if table not in self._tables:
            reservoir = _TableReservoir(reservoir_max_size=self._table_reservoir_max_size)
            self._tables[table] = reservoir

        reservoir.ingest_data(data=data, table_size_estimation=table_estimated_size)

    def build_sample(self) -> typing.Tuple[DataFrame, Estimation]:
        # Returns sample and estimated total size of all tables
        table_to_size_est = {}

        for table, table_reservoir in list(self._tables.items()):
            if not table_reservoir.reservoir_size:
                continue  # Ignore empty reservoirs

            size = table_reservoir.estimate_table_size()
            table_to_size_est[table] = size

        total_size = Estimation.sum_independent_ests(table_to_size_est.values())
        samples: typing.List[DataFrame] = []

        for table, size_est in table_to_size_est.items():
            table_size_ratio = size_est.value / total_size.value
            table_sample = self._tables[table].sample(sample_size=max(int(table_size_ratio * self._table_reservoir_max_size), 1))
            samples.append(table_sample)

        if samples:
            return concat(samples, ignore_index=True), total_size

        return DataFrame(columns=[get_term_column_name(term) for term in self._terms]), total_size

    @property
    def terms(self) -> typing.Set[Term]:
        return set(self._terms)


class _TableReservoir:
    def __init__(self, *, reservoir_max_size: int):
        self._reservoir_max_size = reservoir_max_size
        self._canonical_columns: typing.List[str] | None = None
        self._visited_row_count = 0
        self._row_ids_in_reservoir = set()
        self._reservoir: typing.List[typing.Tuple] = []
        self._table_size_estimations = []

    def ingest_data(self, *, data: DataFrame, table_size_estimation: int) -> None:
        # TODO: use reservoir sampling here
        # TODO: use
        self._table_size_estimations.append(table_size_estimation)

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

            if len(self._reservoir) < self._reservoir_max_size:
                self._reservoir.append(row)
                self._row_ids_in_reservoir.add(row_id)
            else:
                index = random.randint(0, self._visited_row_count)

                if index < self._reservoir_max_size:
                    reservoir_row_id_to_replace = self._reservoir[index][row_id_index]
                    self._row_ids_in_reservoir.remove(reservoir_row_id_to_replace)
                    self._row_ids_in_reservoir.add(row_id)
                    self._reservoir[index] = row

    def sample(self, *, sample_size: int) -> DataFrame:
        if sample_size < 1:
            raise ValueError

        # If the reservoir is smaller than its max size, we scale it artificially by replicating elements.
        if len(self._reservoir) < self._reservoir_max_size:
            scale_factor = self._reservoir_max_size / len(self._reservoir)
            reservoir = scale_sequence(seq=self._reservoir, factor=scale_factor)
        else:
            reservoir = self._reservoir

        sample = random.sample(reservoir, sample_size)

        df = DataFrame(sample)
        df.columns = self._canonical_columns
        df.drop(StatQLInternalColumns.ROW_ID, axis=1, inplace=True)

        return df

    def estimate_table_size(self, *, alpha: float = 0.05, bootstrap_iterations: int = 1000) -> Estimation:
        data = np.array(self._table_size_estimations)
        n = data.shape[0]

        samples = np.random.choice(data, size=(bootstrap_iterations, n), replace=True)

        means = samples.mean(axis=1)

        lower, upper = np.percentile(means, [100 * (alpha / 2), 100 * (1 - alpha / 2)])

        point_estimation = data.mean()

        return Estimation(point_estimation, (upper - lower) / 2)

    @property
    def reservoir_size(self) -> int:
        return len(self._reservoir)
