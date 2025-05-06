"""Integration tests."""

from pathlib import Path
from typing import Any, Hashable

import orjson
import pytest

from tests.integration.json_schema import InputJSON
from src.processor import JSONValidator
from src.processor.errors import InvalidInputError
from tests.config import TestConfig


def generate_input(sample_id: str) -> dict[Hashable, Any]:
    """Generate input to be sent to API."""
    input_: dict[Hashable, Any] = read_input(sample_id=sample_id)
    source_file: dict[Hashable, Any] = read_input(source_file=True)
    input_["sourceFile"] = source_file
    return input_


def read_input(sample_id: str = "", *, source_file: bool = False) -> dict[Hashable, Any]:
    """Read local input files in JSON format."""
    if source_file:
        path_ = Path(f"{TestConfig.INPUT_JSONS_FOLDER}/SourceFile.json")
    elif sample_id:
        path_ = Path(f"{TestConfig.INPUT_JSONS_FOLDER}/input_{sample_id.zfill(3)}.json")
    else:
        raise ValueError

    with path_.open(mode="rb") as input_json:
        return_map: dict[Hashable, Any] = orjson.loads(input_json.read())

    return return_map


@pytest.mark.integration
def test_integration_1() -> None:
    """Test integration 1."""
    input_ = generate_input(sample_id="1")
    with pytest.raises(expected_exception=InvalidInputError):
        JSONValidator(input_=input_, model=InputJSON)


@pytest.mark.integration
def test_integration_2() -> None:
    """Test integration 2."""
    input_ = generate_input(sample_id="2")
    with pytest.raises(expected_exception=InvalidInputError):
        JSONValidator(input_=input_, model=InputJSON)


@pytest.mark.integration
def test_integration_3() -> None:
    """Test integration 3."""
    input_ = generate_input(sample_id="3")
    with pytest.raises(expected_exception=InvalidInputError):
        JSONValidator(input_=input_, model=InputJSON)
