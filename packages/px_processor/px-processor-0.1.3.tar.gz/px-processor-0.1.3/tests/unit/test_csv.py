import pytest

from src.processor import EmptyInputError, InvalidInputError
from src.processor.csv.main import CSVValidator
from tests.config import TestConfig


def test_csv_validator_initialization() -> None:
    csv_paths: list[str] = [f"{TestConfig.INPUT_CSVS_FOLDER}/input_003.csv"]
    data_types: list[str] = ["character", "numeric"]
    column_names: list[str] = ["name", "age"]
    validator = CSVValidator(
        csv_paths=csv_paths,
        data_types=data_types,
        column_names=column_names
    )
    assert validator._csv_paths == csv_paths
    assert validator._data_types == data_types
    assert validator._column_names == column_names


def test_csv_validator_read_pandas() -> None:
    csv_paths: list[str] = [f"{TestConfig.INPUT_CSVS_FOLDER}/input_003.csv"]
    data_types: list[str] = ["character", "numeric"]
    column_names: list[str] = ["name", "age"]
    validator = CSVValidator(
        csv_paths=csv_paths,
        data_types=data_types,
        column_names=column_names,
    )
    assert validator.data is not None

def test_csv_validator_validate() -> None:
    csv_paths: list[str] = [f"{TestConfig.INPUT_CSVS_FOLDER}/input_003.csv"]
    data_types: list[str] = ["character", "numeric"]
    column_names: list[str] = ["name", "age"]
    validator = CSVValidator(
        csv_paths=csv_paths,
        data_types=data_types,
        column_names=column_names
    )
    assert validator.validate() is True

def test_csv_validator_check_missing_data() -> None:
    csv_paths: list[str] = [f"{TestConfig.INPUT_CSVS_FOLDER}/input_003.csv"]
    data_types: list[str] = ["character", "numeric"]
    column_names: list[str] = ["name", "age"]
    columns_with_no_missing_data = ["name"]
    validator = CSVValidator(
        csv_paths=csv_paths,
        data_types=data_types,
        column_names=column_names,
        columns_with_no_missing_data=columns_with_no_missing_data
    )
    validator.data.columns = ["name", "age"]
    assert validator.errors == []

def test_csv_validator_check_fixed_column_values() -> None:
    csv_paths: list[str] = [f"{TestConfig.INPUT_CSVS_FOLDER}/input_003.csv"]
    data_types: list[str] = ["character", "numeric"]
    column_names: list[str] = ["name", "age"]
    valid_column_values: dict[str, list[str]] = {"name": ["Alice", "Bob"]}
    with pytest.raises(expected_exception=InvalidInputError):
        CSVValidator(
            csv_paths=csv_paths,
            data_types=data_types,
            column_names=column_names,
            valid_column_values=valid_column_values
        )
