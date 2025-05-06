from functools import partial
from typing import Any, Dict, Optional
from copy import deepcopy
import mlflow
from kedro.io.core import AbstractDataset, DatasetError
from mlflow.tracking import MlflowClient
from kedro_mlflow.io.models import MlflowModelTrackingDataset
from kedro_sumz.utils.mlflow import ModelWithConfig


class MlflowModelWithConfigDataset(MlflowModelTrackingDataset):
    """
    Wrapper for saving, logging and loading for all MLFlow model flavor
    including its configuration
    """

    def __init__(
        self,
        flavor: str,
        run_id: Optional[str] = None,
        artifact_path: Optional[str] = "model",
        pyfunc_workflow: Optional[str] = None,
        load_args: Optional[Dict[str, Any]] = None,
        save_args: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initializes MlflowModelWithConfigDataSet

        Args:
            flavor (str): Flavor of the model
            run_id (Optional[str], optional): Mlflow run id. Defaults to None.
            artifact_path (Optional[str], optional): Path of the model artifact. Defaults to "model".
            pyfunc_workflow (Optional[str], optional): Name of the pyfunc model. Defaults to None.
            load_args (Optional[Dict[str, Any]], optional): Load args used in the
            mlflow load_model function. Defaults to None.
            save_args (Optional[Dict[str, Any]], optional): Save args used in the
            mlflow log_model function. Defaults to None.
        """
        super().__init__(
            flavor, run_id, artifact_path, pyfunc_workflow, load_args, save_args
        )

    def _save_model_in_run(self, model: ModelWithConfig):
        """
        Saves a model in a run as an artifact

        Args:
            model (ModelWithConfig): Object which stores the model and its configuration

        Raises:
            DataSetError: When the object passed is not an instance of the ModelWithConfig class
        """
        if not isinstance(model, ModelWithConfig):
            raise DatasetError(
                "The model to be logged must be an instance of the ModelWithConfig class"
            )

        if not self._logging_activated:
            return

        save_args = self._prepare_save_args(model_with_config=model)

        if self._flavor == "mlflow.pyfunc":
            # PyFunc models utilise either `python_model` or `loader_module`
            # workflow. We we assign the passed `model` object to one of those keys
            # depending on the chosen `pyfunc_workflow`.
            save_args[self._pyfunc_workflow] = model.model
            self._mlflow_model_module.log_model(**save_args)
        else:
            # Otherwise we save using the common workflow
            self._mlflow_model_module.log_model(model.model, **save_args)

    def _prepare_save_args(self, model_with_config: ModelWithConfig) -> Dict[str, Any]:
        save_args = deepcopy(self._save_args)

        save_args["signature"] = self._save_arg_value(
            catalog_save_arg=self._save_args.get("signature"),
            model_with_config_arg=model_with_config.signature,
        )

        save_args["conda_env"] = self._save_arg_value(
            catalog_save_arg=self._save_args.get("conda_env"),
            model_with_config_arg=model_with_config.conda_env,
        )

        save_args["pip_requirements"] = self._save_arg_value(
            catalog_save_arg=self._save_args.get("pip_requirements"),
            model_with_config_arg=model_with_config.pip_requirements,
        )

        save_args["extra_pip_requirements"] = self._save_arg_value(
            catalog_save_arg=self._save_args.get("extra_pip_requirements"),
            model_with_config_arg=model_with_config.extra_pip_requirements,
        )

        save_args["artifact_path"] = self._artifact_path

        return save_args

    def _save_arg_value(self, catalog_save_arg: Any, model_with_config_arg: Any) -> Any:
        if catalog_save_arg is None and model_with_config_arg is None:
            return None
        elif catalog_save_arg is None:
            return model_with_config_arg
        else:
            return catalog_save_arg


class MlflowMetricsDictDataset(AbstractDataset):
    """This class represent MLflow metrics dictionary dataset."""

    def __init__(
        self,
        prefix: str = None,
        run_id: str = None,
        metadata: Dict[str, Any] = None,
    ):
        """Initialise MlflowMetricsDictDataSet.

        Args:
            prefix (str, optional): Prefix for metrics logged in MLflow. Defaults to None
            run_id (str, optional): ID of MLflow run. Defaults to None
            metadata: Any arbitrary metadata.
                This is ignored by Kedro, but may be consumed by users or external plugins.
        """
        self._prefix = prefix
        self.run_id = run_id
        self._logging_activated = True  # by default, logging is activated!
        self.metadata = metadata

    @property
    def run_id(self):
        """Get run id.

        If active run is not found, tries to find last experiment.

        Raise `DataSetError` exception if run id can't be found.

        Returns:
            str: String contains run_id.
        """
        if self._run_id is not None:
            return self._run_id
        run = mlflow.active_run()
        if run:
            return run.info.run_id
        raise DatasetError("Cannot find run id.")

    @run_id.setter
    def run_id(self, run_id):
        self._run_id = run_id

    # we want to be able to turn logging off for an entire pipeline run
    # To avoid that a single call to a dataset in the catalog creates a new run automatically
    # we want to be able to turn everything off
    @property
    def _logging_activated(self):
        return self.__logging_activated

    @_logging_activated.setter
    def _logging_activated(self, flag):
        if not isinstance(flag, bool):
            raise ValueError(f"_logging_activated must be a boolean, got {type(flag)}")
        self.__logging_activated = flag

    def _load(self) -> Dict[str, float]:
        """Load MlflowMetricsDictDataSet.

        Returns:
            Dict[str, float]: Dictionary with MLflow metrics.
        """
        all_metrics = self._get_all_metrics()

        dataset_metrics = self._filter_dataset_metrics(all_metrics)

        if not dataset_metrics:
            raise DatasetError(
                "Tried to load an empty metrics dictionary"
                f"be sure that metrics with the prefix '{self._prefix}' exists"
                "in the current run"
            )

        return dataset_metrics

    def _save(self, data: Dict[str, float]) -> None:
        """
        Save given MLflow metrics dictionary dataset
        and log it in MLflow as metrics.

        Args:
            data (Dict[str, float]): Metrics dictionary.
        """
        if not data:
            raise DatasetError("Metrics dictionary should have at least one metric")

        client = MlflowClient()
        try:
            run_id = self.run_id
        except DatasetError:
            # If run_id can't be found log_metric would create new run.
            run_id = None

        log_metric = (
            partial(client.log_metric, run_id)
            if run_id is not None
            else mlflow.log_metric
        )

        if not all([isinstance(value, float) for value in data.values()]):
            raise DatasetError(f"All metric values should be of type `float`")

        metrics = {f"{self._prefix}.{key}": value for key, value in data.items()}

        if self._logging_activated:
            for k, v in metrics.items():
                log_metric(k, v)

    def _exists(self) -> bool:
        """Check if MLflow metrics dataset exists.

        Returns:
            bool: Is MLflow metrics dataset exists?
        """
        all_metrics = self._get_all_metrics()
        dataset_metrics = self._filter_dataset_metrics(all_metrics)
        return len(dataset_metrics.keys()) > 0

    def _describe(self) -> Dict[str, Any]:
        """Describe MLflow metrics dataset.

        Returns:
            Dict[str, Any]: Dictionary with MLflow metrics
            dictionary dataset description.
        """
        return {
            "run_id": self._run_id,
            "prefix": self._prefix,
        }

    def _filter_dataset_metrics(self, metrics: Dict[str, float]) -> Dict[str, float]:
        """
        Filter a metric dictionary by keeping only those that
        belongs to the dataset

        Args:
            metric (Dict[str, float]): Metrics dictionary.
        Returns:
            Dict[str, float]: Dictionary with the metrics that belongs
            to the dataset
        """
        dataset_metrics = {
            k: v for k, v in metrics.items() if k.startswith(self._prefix)
        }

        return dataset_metrics

    def _get_all_metrics(self) -> Dict[str, float]:
        """Retrieve all metrics logged in the current run

        Returns:
            Dict[str, float]: Dictionary with all the metrics logged
            in the current run
        """
        client = MlflowClient()
        run = client.get_run(self.run_id)
        return run.data.metrics
