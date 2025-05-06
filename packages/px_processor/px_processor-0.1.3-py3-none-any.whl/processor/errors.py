"""Custom exceptions for the validator module."""

from collections.abc import Hashable
from typing import Any

from src.processor.config import CSVConfig

CSVConfig = CSVConfig()


class _ValidationError(Exception):
    """Base class for all validation errors."""

    def __init__(self, message: str) -> None:
        """Initialise the object."""
        self.message: str = message
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return a string representation of the object.

        Returns:
            str: A string representation of the object.

        """
        return self.message

    def __repr__(self) -> str:
        """Return a string representation of the object.

        Returns:
            str: A string representation of the object.

        """
        return self.__str__()

    def __bool__(self) -> bool:
        """Return a boolean representation of the object.

        Returns:
            bool: True if the message is not empty, False otherwise

        """
        return bool(self.message)


class InvalidKeyError(_ValidationError):
    """Raised when a key is invalid."""

    def __init__(self, key: Hashable) -> None:
        """Initialise the object."""
        self.key: Hashable = key
        message: str = f"Invalid key: {key}"
        super().__init__(message=message)


class InvalidValueError(_ValidationError):
    """Raised when a value is invalid."""

    def __init__(self, value: str) -> None:
        """Initialise the object."""
        self.value: str = value
        message: str = f"Invalid value: {value}"
        super().__init__(message=message)


class InvalidTypeError(_ValidationError):
    """Raised when a type is invalid."""

    def __init__(self, type_: str) -> None:
        """Initialise the object."""
        self.type_: str = type_
        message: str = f"Invalid type: {type_}"
        super().__init__(message=message)


class InvalidInputError(_ValidationError):
    """Invalid input."""

    def __init__(self, message: str) -> None:
        """Initialise the object."""
        self.message: str = (
            f"\n\nInput validation failed due to the following errors: \n\n{message}"
        )
        super().__init__(message=self.message)


class InvalidDateFormatError(_ValidationError):
    """Raised when a date format is invalid."""

    def __init__(self, column: str) -> None:
        """Initialise the object."""
        error_message: str = (
            f"All values in '{column}' should follow {CSVConfig.DATE_FORMAT} format."
        )
        super().__init__(message=error_message)


class FixedValueColumnError(_ValidationError):
    """Raised when a fixed value column has invalid values."""

    def __init__(self, column: str, valid_values: list[str]) -> None:
        """Initialise the object."""
        error_message: str = f"Valid values for '{column}' column are {valid_values}."
        super().__init__(message=error_message)


class MissingDataError(_ValidationError):
    """Raised when a column has missing data."""

    def __init__(self, column: str, rows: list[Any]) -> None:
        """Initialise the object."""
        error_message: str = f"Missing data in '{column}' column in rows: {rows}."
        super().__init__(message=error_message)


class MissingColumnError(_ValidationError):
    """Raised when a column is missing."""

    def __init__(self, column: str) -> None:
        """Initialise the object."""
        error_message: str = f"The '{column}' column could not be found."
        super().__init__(message=error_message)


class MissingPathsError(_ValidationError):
    """Raised when file-paths are missing."""

    def __init__(self) -> None:
        """Initialise the object."""
        error_message: str = "Empty file-paths."
        super().__init__(message=error_message)


class UniqueValueError(_ValidationError):
    """Raised when a column has duplicate values."""

    def __init__(self, column: str) -> None:
        """Initialise the object."""
        error_message: str = f"Duplicate values in '{column}'."
        super().__init__(message=error_message)


class EmptyInputError(_ValidationError):
    """Empty input error."""

    def __init__(self) -> None:
        """Initialise the object."""
        self.message: str = "Empty input. Please provide a non-empty input."
        super().__init__(message=self.message)
