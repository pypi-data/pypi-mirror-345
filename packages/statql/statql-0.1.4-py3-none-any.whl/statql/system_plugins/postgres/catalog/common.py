import typing

from statql.common import FrozenModel


class DatabaseIdentifier(FrozenModel):
    cluster_name: str
    db_name: str

    def __str__(self):
        return f"{self.cluster_name}:{self.db_name}"


class PostgresTableIdentifier(FrozenModel):
    cluster_name: str
    db_name: str
    schema_name: str
    table_name: str

    @property
    def db_identifier(self) -> DatabaseIdentifier:
        return DatabaseIdentifier(cluster_name=self.cluster_name, db_name=self.db_name)

    def __str__(self):
        return f"{self.cluster_name}:{self.db_name}:{self.schema_name}:{self.table_name}"


class PostgresTableInfo(FrozenModel):
    table_identifier: PostgresTableIdentifier
    column_names: typing.AbstractSet[str]
