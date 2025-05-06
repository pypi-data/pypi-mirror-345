"""Dummy dataset for testing purposes."""
from typing import Any

from kedro.io.memory_dataset import MemoryDataset


class DummyDataset(MemoryDataset):
    """Dummy dataset for testing purposes."""

    # pylint: disable=useless-super-delegation,too-few-public-methods
    def __init__(
        self,
        data: Any = True,
        copy_mode: str = None,
        metadata: dict[str, Any] | None = None,
    ):
        super().__init__(data, copy_mode, metadata)
