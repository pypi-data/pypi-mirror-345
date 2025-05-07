"""``AbstractDataSet`` implementation to access Spark dataframes using
``pyspark`` on Apache Hive.
"""
import importlib
import pickle
from copy import deepcopy
from pathlib import PurePosixPath
from typing import Any, Dict
from warnings import warn

from kedro_datasets.spark.spark_dataset import (
    _split_filepath,
    _strip_dbfs_prefix,
)
from kedro.io.core import (
    AbstractDataset,
    DatasetError,
)
from pyspark.ml import PipelineModel

from pyspark.ml.util import GeneralJavaMLWritable
from pyspark.sql import DataFrame, SparkSession

from pyspark.sql.utils import AnalysisException
from s3fs import S3FileSystem


# pylint:disable=too-many-instance-attributes
class SparkRegressionModelDataset(AbstractDataset):
    """``SparkRegressionModelDataSet`` loads and saves spark ml regression models."""

    _SINGLE_PROCESS = True
    DEFAULT_SAVE_ARGS = {}  # type: Dict[str, Any]
    DEFAULT_LOAD_ARGS = {}  # type: Dict[str, Any]

    # pylint:disable=too-many-arguments
    def __init__(
        self,
        filepath: str,
        credentials: Dict[str, Any] = None,
        load_args: Dict[str, Any] = None,
        save_args: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None,
    ) -> None:
        """Creates a new instance of ``SparkRegressionModelDataSet``.

        Args:
            filepath: Path to the saved model.
            credentials: Credentials required to get access to the filesystem.
            dataset_type: Type of the dataset. Can be either "table" or "file".
            load_args: Load args passed to Spark LinearRegressionModel
            save_args: Optional mapping of any options,
                passed to the LinearRegressionModel save method.
            metadata: Any arbitrary metadata.
                This is ignored by Kedro, but may be consumed by users or external plugins.

        Raises:
            DataSetError: Invalid configuration supplied
        """
        credentials = deepcopy(credentials) or {}
        self.metadata = metadata
        fs_prefix, filepath = _split_filepath(filepath)
        if fs_prefix in ("s3a://", "s3n://"):
            if fs_prefix == "s3n://":
                warn(
                    "`s3n` filesystem has now been deprecated by Spark, "
                    "please consider switching to `s3a`",
                    DeprecationWarning,
                )
            _s3 = S3FileSystem(**credentials)
            path = PurePosixPath(filepath)
        else:
            path = PurePosixPath(filepath)

        self._filepath = path
        self._fs_prefix = fs_prefix
        # Handle default load and save arguments
        self._load_args = deepcopy(self.DEFAULT_LOAD_ARGS)
        if load_args is not None:
            self._load_args.update(load_args)
        self._save_args = deepcopy(self.DEFAULT_SAVE_ARGS)
        if save_args is not None:
            self._save_args.update(save_args)

        self._supported_modes = {
            "overwrite",
            "error",
            "errorifexists",
            "ignore",
        }
        self._write_mode = self._save_args.pop("mode", "errorifexists")
        self._handle_write_mode()

    def _describe(self) -> Dict[str, Any]:
        return {
            "filepath": self._fs_prefix + str(self._filepath),
            "load_args": self._load_args,
            "save_args": self._save_args,
        }

    @staticmethod
    def _get_spark() -> SparkSession:
        """Get the active Spark session."""
        return SparkSession.getActiveSession()

    def _exists(self) -> bool:
        try:
            self._load()
        except AnalysisException as exception:
            if (
                exception.desc.startswith("Path does not exist:")
                or "is not a Delta table" in exception.desc
            ):
                return False
            raise
        return True

    def _load(self) -> DataFrame:
        load_path = _strip_dbfs_prefix(self._fs_prefix + str(self._filepath))
        regression_module = importlib.import_module("pyspark.ml.regression")
        cls = getattr(
            regression_module,
            self._load_args.get("regression_model", "LinearRegressionModel"),
        )
        return cls.load(load_path)

    def _save(self, data: GeneralJavaMLWritable) -> None:
        save_path = _strip_dbfs_prefix(self._fs_prefix + str(self._filepath))
        if self._write_mode == "overwrite":
            data.write().overwrite().save(save_path)
        elif self._write_mode == "error":
            raise DatasetError(
                f"It is not possible to perform 'save()' "
                f"with mode '{self._write_mode}' on 'SparkModelDataSet'. "
            )
        else:
            data.write().save(save_path)

    def _handle_write_mode(self) -> None:
        if self._write_mode and self._write_mode not in self._supported_modes:
            raise DatasetError(
                f"It is not possible to perform 'save()' "
                f"with mode '{self._write_mode}' on 'SparkModelDataSet'. "
            )

    def __getstate__(self) -> None:
        raise pickle.PicklingError(
            "PySpark datasets objects cannot be pickled "
            "or serialised as Python objects."
        )


# pylint:disable=too-many-instance-attributes
class SparkPipelineModelDataset(AbstractDataset):
    """``SparkPipelineModelDataSet`` loads and saves spark ml pipeline models."""

    _SINGLE_PROCESS = True
    DEFAULT_SAVE_ARGS = {}  # type: Dict[str, Any]
    DEFAULT_LOAD_ARGS = {}  # type: Dict[str, Any]

    # pylint:disable=too-many-arguments
    def __init__(
        self,
        filepath: str,
        credentials: Dict[str, Any] = None,
        load_args: Dict[str, Any] = None,
        save_args: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None,
    ) -> None:
        """Creates a new instance of ``SparkPipelineModelDataSet``.

        Args:
            filepath: Path to the saved model.
            credentials: Credentials required to get access to the filesystem.
            load_args: Load args passed to Spark LinearRegressionModel
            save_args: Optional mapping of any options,
                passed to the LinearRegressionModel save method.
            metadata: Any arbitrary metadata.
                This is ignored by Kedro, but may be consumed by users or external plugins.

        Raises:
            DataSetError: Invalid configuration supplied
        """
        credentials = deepcopy(credentials) or {}
        self.metadata = metadata
        fs_prefix, filepath = _split_filepath(filepath)
        if fs_prefix in ("s3a://", "s3n://"):
            if fs_prefix == "s3n://":
                warn(
                    "`s3n` filesystem has now been deprecated by Spark, "
                    "please consider switching to `s3a`",
                    DeprecationWarning,
                )
            _s3 = S3FileSystem(**credentials)
            path = PurePosixPath(filepath)
        else:
            path = PurePosixPath(filepath)

        self._filepath = path
        self._fs_prefix = fs_prefix
        # Handle default load and save arguments
        self._load_args = deepcopy(self.DEFAULT_LOAD_ARGS)
        if load_args is not None:
            self._load_args.update(load_args)
        self._save_args = deepcopy(self.DEFAULT_SAVE_ARGS)
        if save_args is not None:
            self._save_args.update(save_args)

        self._supported_modes = {
            "overwrite",
            "error",
            "errorifexists",
            "ignore",
        }
        self._write_mode = self._save_args.pop("mode", "errorifexists")
        self._handle_write_mode()

    def _describe(self) -> Dict[str, Any]:
        return {
            "filepath": self._fs_prefix + str(self._filepath),
            "load_args": self._load_args,
            "save_args": self._save_args,
        }

    @staticmethod
    def _get_spark() -> SparkSession:
        """Get the active Spark session."""
        return SparkSession.getActiveSession()

    def _exists(self) -> bool:
        try:
            self._load()
        except AnalysisException as exception:
            if (
                exception.desc.startswith("Path does not exist:")
                or "is not a Delta table" in exception.desc
            ):
                return False
            raise
        return True

    def _load(self) -> DataFrame:
        load_path = _strip_dbfs_prefix(self._fs_prefix + str(self._filepath))
        return PipelineModel.load(load_path)

    def _save(self, data: GeneralJavaMLWritable) -> None:
        save_path = _strip_dbfs_prefix(self._fs_prefix + str(self._filepath))
        if self._write_mode == "overwrite":
            data.write().overwrite().save(save_path)
        elif self._write_mode == "error":
            raise DatasetError(
                f"It is not possible to perform 'save()' "
                f"with mode '{self._write_mode}' on 'SparkPipelineModelDataSet'. "
            )
        else:
            data.write().save(save_path)

    def _handle_write_mode(self) -> None:
        if self._write_mode and self._write_mode not in self._supported_modes:
            raise DatasetError(
                f"It is not possible to perform 'save()' "
                f"with mode '{self._write_mode}' on 'SparkPipelineModelDataSet'. "
            )

    def __getstate__(self) -> None:
        raise pickle.PicklingError(
            "PySpark datasets objects cannot be pickled "
            "or serialised as Python objects."
        )
