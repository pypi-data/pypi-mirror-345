"""Input model blueprint for JSON data."""

from collections.abc import Hashable
from typing import Any

from pydantic import BaseModel, Field, field_validator


class InputJSON(BaseModel):
    """Schema for JSON objects."""

    form: dict[Hashable, Any] = Field(strict=True)
    schema_information: dict[Hashable, Any] = Field(strict=True, alias="schemaInformation")
    parameters: dict[Hashable, Any] = Field(strict=True)
    result_file: dict[Hashable, Any] = Field(strict=True, alias="resultFile")
    source_file: dict[Hashable, Any] = Field(strict=True, alias="sourceFile")
    script_path: str = Field(strict=True, alias="scriptPath")
    executed_by: str = Field(strict=True, alias="executedBy")
    source_directory: str = Field(
        alias="sourceDirectory",
    )

    @field_validator("form")
    @classmethod
    def simple_validation(cls, value: dict[Hashable, Any]) -> dict[Hashable, Any]:
        """Validate the form.

        Parameters
        ----------
        value: dict[Hashable, Any]
                The form to validate.

        Returns
        -------
        dict[Hashable, Any]: The validated form.

        Raises
        ------
        ValueError: If the form is empty

        """
        if not value:
            error_message: str = "Form cannot be empty."
            raise ValueError(error_message)
        return value
