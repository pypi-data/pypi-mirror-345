"""Context hooks for the Virgo project."""
from typing import Any, Dict, List, Callable

from kedro.framework.hooks import hook_impl
from kedro.io import DataCatalog
from kedro_sumz.extras.context import KedroSparkContext
from kedro_sumz.utils import CurrentKedroContext

try:
    from kedro_sumz.extras.datasets.mlflow import MlflowMetricsDictDataset
except ImportError:
    pass


class ContextHooks:  # pylint: disable=too-few-public-methods
    """Context hooks."""

    def __init__(self, callbacks: List[Callable[["KedroSparkContext"], None]] = None):
        callbacks = callbacks if callbacks else []
        self._callbacks = callbacks

    @hook_impl
    def after_context_created(self, context: "KedroSparkContext") -> None:
        """Stores the current kedro context inside a singleton class.

        Args:
            context: The current Kedro context.
        """
        _ = CurrentKedroContext(context)
        for c in self._callbacks:
            c(context)


class MLFLowHooks:  # pylint: disable=too-few-public-methods
    """MLFLow hooks."""

    @hook_impl
    def after_catalog_created(
        self,
        catalog: DataCatalog,
        conf_catalog: Dict[str, Any],
        conf_creds: Dict[str, Any],
        feed_dict: Dict[str, Any],
        save_version: str,
        load_versions: str,
    ):
        """Hook to add the mlflow dataset to the catalog."""
        # we use this hooks to modif "MlflowMetricsDictDataSet" to ensure consistency
        # of the metric name with the catalog name
        for name, dataset in catalog._data_sets.items():
            if (
                isinstance(dataset, MlflowMetricsDictDataset)
                and dataset._prefix is None
            ):
                if dataset._run_id is not None:
                    catalog._data_sets[name] = MlflowMetricsDictDataset(
                        run_id=dataset._run_id, prefix=name
                    )
                else:
                    catalog._data_sets[name] = MlflowMetricsDictDataset(prefix=name)
