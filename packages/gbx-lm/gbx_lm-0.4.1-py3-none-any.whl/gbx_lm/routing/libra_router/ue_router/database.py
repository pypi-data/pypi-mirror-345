import torch
from typing import List, Type, Any, Dict

import gzip
import sys
import json
import peewee as pw
from safetensors.torch import save as st_save, load as st_load

# Create a database proxy that can be initialized later
db_proxy = pw.DatabaseProxy()
_metrics = None


class _BaseMetric(pw.Model):
    """This is the base class for all metrics, which includes using the database proxy."""

    model = pw.CharField()
    variable = pw.CharField()
    version = pw.IntegerField()
    data = pw.BlobField()

    class Meta:
        database = db_proxy


class MahalanobisDistance(_BaseMetric):
    pass


def metrics() -> List[Type[_BaseMetric]]:
    """Get a list of all implemented metrics."""

    global _metrics
    if _metrics is None:
        _metrics = set()
        candidates = sys.modules[__name__].__dict__
        for name, var in candidates.items():
            if isinstance(var, type) and issubclass(var, _BaseMetric) and var is not _BaseMetric:
                _metrics.add(var)
    return list(_metrics)


class TensorDatabase:
    """A database based on peewee to store different metrics through a database connection."""
    def __init__(self, database) -> None:
        self.database = database
        db_proxy.initialize(database)
        self.database.connect()
        self.database.bind(metrics())
        self.database.create_tables(metrics())

    def close(self) -> None:
        self.database.close()

    @staticmethod
    def save_tensor(tensor: torch.Tensor, metric: Type[_BaseMetric], model_name: str, variable_name: str, version: int = None, overwrite: bool = False) -> None:
        assert metric in metrics(), f"The given metric {metric} is unknown."

        if version is None:
            # if no version is given, automatically choose the maximum version + 1 to save the tensor
            # if overwrite is True, instead choose maximum version

            query = metric.select(pw.fn.MAX(metric.version).alias('max_version')).where(
                (metric.model == model_name) &
                (metric.variable == variable_name)
            )
            max_version = query.scalar() or 0
            version = max_version + 1
            if overwrite:
                version = max_version

        # check if an entry with the given version exists
        existing_entry = metric.select().where(
            (metric.model == model_name) &
            (metric.variable == variable_name) &
            (metric.version == version)
        ).exists()

        if existing_entry and not overwrite:
            raise ValueError(f"An entry with model '{model_name}', variable '{variable_name}', and version '{version}' already exists. Set overwrite to True to overwrite it.")

        if existing_entry:
            metric.delete().where(
                (metric.model == model_name) &
                (metric.variable == variable_name) &
                (metric.version == version)
            ).execute()

        metric.create(
            model=model_name,
            variable=variable_name,
            version=version,
            data=TensorDatabase._save(tensor),
        )

    @staticmethod
    def load_tensor(metric: Type[_BaseMetric], model_name: str, variable_name: str, version: int = None) -> torch.Tensor:
        assert metric in metrics(), f"The given metric {metric} is unknown."
        if version is None:
            # query the latest version if none is specified
            entry = metric.select().where(
                (metric.model == model_name)
                & (metric.variable == variable_name)
            ).order_by(metric.version.desc()).get()
            return TensorDatabase._load(entry.data)

        entry = metric.get(
            (metric.model == model_name)
            & (metric.variable == variable_name)
            & (metric.version == version)
        )
        return TensorDatabase._load(entry.data)

    @staticmethod
    def save_json(data: Dict[str, Any], metric: Type[_BaseMetric], model_name: str,
                  variable_name: str, version: int = None, overwrite: bool = False) -> None:
        """Save JSON data to database"""
        assert metric in metrics(), f"The given metric {metric} is unknown."

        if version is None:
            query = metric.select(pw.fn.MAX(metric.version).alias('max_version')).where(
                (metric.model == model_name) &
                (metric.variable == variable_name)
            )
            max_version = query.scalar() or 0
            version = max_version + 1
            if overwrite:
                version = max_version

        existing_entry = metric.select().where(
            (metric.model == model_name) &
            (metric.variable == variable_name) &
            (metric.version == version)
        ).exists()

        if existing_entry and not overwrite:
            raise ValueError(f"An entry with model '{model_name}', variable '{variable_name}', "
                             f"and version '{version}' already exists. Set overwrite to True to overwrite it.")

        if existing_entry:
            metric.delete().where(
                (metric.model == model_name) &
                (metric.variable == variable_name) &
                (metric.version == version)
            ).execute()

        json_str = json.dumps(data)
        compressed_data = gzip.compress(json_str.encode('utf-8'))

        metric.create(
            model=model_name,
            variable=variable_name,
            version=version,
            data=compressed_data,
        )

    @staticmethod
    def load_json(metric: Type[_BaseMetric], model_name: str, variable_name: str,
                  version: int = None) -> Dict[str, Any]:
        """Load JSON data from database"""
        assert metric in metrics(), f"The given metric {metric} is unknown."

        if version is None:
            entry = metric.select().where(
                (metric.model == model_name) &
                (metric.variable == variable_name)
            ).order_by(metric.version.desc()).get()
        else:
            entry = metric.get(
                (metric.model == model_name) &
                (metric.variable == variable_name) &
                (metric.version == version)
            )

        decompressed_data = gzip.decompress(entry.data)
        return json.loads(decompressed_data.decode('utf-8'))

    @staticmethod
    def _load(data: Any) -> torch.Tensor:
        decompressed_data = gzip.decompress(data)
        tensor_dict = st_load(decompressed_data)
        return tensor_dict["data"]

    @staticmethod
    def _save(tensor: torch.Tensor) -> Any:
        tensor_dict = {"data": tensor}
        formatted_data = st_save(tensor_dict)
        return gzip.compress(formatted_data)


# file based database
class TensorSqliteDatabase(TensorDatabase):
    def __init__(self, file_path, *args, **kwargs):
        database = pw.SqliteDatabase(file_path, *args, **kwargs)
        super().__init__(database)


# in-memory database
class TempInMemoryDatabase(TensorDatabase):
    def __init__(self):
        database = pw.SqliteDatabase(":memory:")
        super().__init__(database)
