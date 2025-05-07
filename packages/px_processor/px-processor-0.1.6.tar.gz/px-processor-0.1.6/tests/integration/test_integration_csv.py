"""Integration tests."""

import pytest

from src.processor.errors import InvalidInputError
from src.processor import CSVValidator
from tests.config import TestConfig



@pytest.fixture
def csv_paths_4() -> list[str]:
    """Return csv paths (for optimisation)."""
    return [f"{TestConfig.INPUT_CSVS_FOLDER}/input_007.csv"]

