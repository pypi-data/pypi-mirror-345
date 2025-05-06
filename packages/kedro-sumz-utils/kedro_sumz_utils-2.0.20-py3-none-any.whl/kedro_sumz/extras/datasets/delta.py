"""``AbstractDataSet`` implementation to access DeltaTables using
``delta-spark``
"""
from pathlib import PurePosixPath
from typing import NoReturn, Dict, Any

from delta.tables import DeltaTable

# pylint: disable=unused-import
from kedro_datasets.spark import SparkHiveDataset  # noqa: F401
from kedro_datasets.spark.spark_dataset import (
    _split_filepath,
    _strip_dbfs_prefix,
)
from kedro.io.core import AbstractDataset, DatasetError
from pyspark.sql import SparkSession
from pyspark.sql.utils import AnalysisException

from kedro_sumz.utils import get_kedro_context


class DeltaTableDataset(AbstractDataset[None, DeltaTable]):
    """``DeltaTableDataSet`` loads data into DeltaTable objects.

    Example usage for the
    `YAML API <https://kedro.readthedocs.io/en/stable/data/\
    data_catalog.html#use-the-data-catalog-with-the-yaml-api>`_:

    .. code-block:: yaml

        weather@spark:
          type: spark.SparkDataSet
          filepath: data/02_intermediate/data.parquet
          file_format: "delta"

        weather@delta:
          type: virgo.extras.datasets.DeltaTableDataSet
          directory: data/02_intermediate
          table: "data.parquet"

        weather_table@delta:
          type: virgo.extras.datasets.delta.DeltaTableDataSet
          directory: intermediate
          table: data

    Example usage for the
    `Python API <https://kedro.readthedocs.io/en/stable/data/\
    data_catalog.html#use-the-data-catalog-with-the-code-api>`_:
    ::

        >>> from pyspark.sql import SparkSession
        >>> from pyspark.sql.types import (StructField, StringType,
        >>>                                IntegerType, StructType)
        >>>
        >>> from kedro_datasets.spark import DeltaTableDataset, SparkDataset
        >>>
        >>> schema = StructType([StructField("name", StringType(), True),
        >>>                      StructField("age", IntegerType(), True)])
        >>>
        >>> data = [('Alex', 31), ('Bob', 12), ('Clarke', 65), ('Dave', 29)]
        >>>
        >>> spark_df = SparkSession.builder.getOrCreate().createDataFrame(data, schema)
        >>>
        >>> data_set = SparkHiveDataset(database="test_database", table="test_table",
        >>>                             write_mode="overwrite")
        >>> data_set.save(spark_df)
        >>> delta_dataset = DeltaTableDataset(directory="test_database", table="test_table")
        >>> delta_table = delta_dataset.load()
        >>>
        >>> delta_table.update()
    """

    # this dataset cannot be used with ``ParallelRunner``,
    # therefore it has the attribute ``_SINGLE_PROCESS = True``
    # for parallelism within a Spark pipeline please consider
    # using ``ThreadRunner`` instead
    _SINGLE_PROCESS = True

    def __init__(
        self,
        directory: str,
        table: str,
        dataset_type: str = None,
        metadata: Dict[str, Any] = None,
    ) -> None:
        """Creates a new instance of ``DeltaTableDataSet``.

        Args:
            directory: Base path to a folder or a database.
            table: Name of the table or file.
            dataset_type: Type of the dataset. Can be either "table" or "file".
            metadata: Any arbitrary metadata.
                This is ignored by Kedro, but may be consumed by users or external plugins.
        """
        self.metadata = metadata
        if not dataset_type and ("/" in directory or "/" in table):
            self._type = "file"
        elif not dataset_type and "." in directory:
            self._type = "table"
        else:
            self._type = dataset_type
        if not self._type:
            raise DatasetError(
                "Could not determine dataset type. Please specify it explicitly."
            )
        if self._type == "table":
            path = f"{directory}.{table}"
            self._database = ".".join(path.split(".")[:-1])
            self._table = table
            self._full_table_address = f"{self._database}.{self._table}"
        else:
            path = f"{directory}/{table}"
            fs_prefix, filepath = _split_filepath(path)
            self._fs_prefix = fs_prefix
            self._filepath = PurePosixPath(filepath)
            self._full_table_address = (
                f"delta.`{self._fs_prefix + str(self._filepath)}`"
            )
            self._type = "file"

    @staticmethod
    def _get_spark() -> SparkSession:
        """Get the active Spark session."""
        if hasattr(get_kedro_context(), "spark_session"):
            return get_kedro_context().spark_session
        else:
            SparkSession.getActiveSession()

    def _load(self) -> DeltaTable:
        return DeltaTable.forName(self._get_spark(), self._full_table_address)

    def _save(self, data: None) -> NoReturn:
        raise DatasetError(f"{self.__class__.__name__} is a read only dataset type")

    def _exists(self) -> bool:
        # noqa # pylint:disable=protected-access
        if self._type == "table":
            return (
                self._get_spark()
                ._jsparkSession.catalog()
                .tableExists(self._database, self._table)
            )

        load_path = _strip_dbfs_prefix(self._fs_prefix + str(self._filepath))

        try:
            self._get_spark().read.load(path=load_path, format="delta")
        except AnalysisException as exception:
            if "is not a Delta table" in exception.desc:
                return False
            raise

        return True

    def _describe(self):
        return {
            "full_table_address": self._full_table_address,
        }
