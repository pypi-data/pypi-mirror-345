"""Validator module for validating CSV files."""

import concurrent.futures
from collections.abc import Callable
from importlib import util
from typing import TYPE_CHECKING, Any

from src.processor.base import BaseValidator
from src.processor.config import PandasConfig, PlatformXMapping
from src.processor.errors import (
    FixedValueColumnError,
    InvalidDateFormatError,
    InvalidInputError,
    MissingColumnError,
    MissingDataError,
    MissingPathsError,
    UniqueValueError,
)

_HAS_PANDAS: bool = util.find_spec(name="pandas") is not None
_HAS_POLARS: bool = util.find_spec(name="polars") is not None

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl


class CSVValidator(BaseValidator):
    """Validator for CSV files.

    Parameters
    ----------
    csv_paths: list[str]
        List of csv paths.
    data_types: list[str]
        List of data types.
    column_names: list[str]
        List of column names.
    columns_with_no_missing_data: list[str], optional
        List of columns with no missing data.
    missing_data_column_mapping: dict[str, list[str]], optional
        Mapping of columns with missing data.
    valid_column_values: dict[str, list[str]], optional
        Mapping of valid column values.
    engine: str, optional
        Engine to use.
    strict_validation: bool, optional
        Whether to use strict validation.

    Raises
    ------
        InvalidInputError: If the CSV data is invalid.

    """

    def __init__(
        self,
        *,
        csv_paths: list[str],
        data_types: list[str],
        column_names: list[str],
        unique_value_columns: list[str] | None = None,
        columns_with_no_missing_data: list[str] | None = None,
        missing_data_column_mapping: dict[str, list[str]] | None = None,
        valid_column_values: dict[str, list[str]] | None = None,
        drop_columns: list[str] | None = None,
        strict_validation: bool = True,
        data_frame_engine: str | None = None,
        pandas_config: PandasConfig | None = None,
        platform_x_mapping: PlatformXMapping | None = None,
    ) -> None:
        """Initialise the object.

        Parameters
        ----------
        csv_paths: list[str]
            List of csv paths.
        data_types: list[str]
            List of data types.
        column_names: list[str]
            List of column names.
        unique_value_columns: list[str], optional
            List of unique value columns.
        columns_with_no_missing_data: list[str], optional
            List of columns with no missing data.
        missing_data_column_mapping: dict[str, list[str]], optional
            Mapping of columns with missing data.
        valid_column_values: dict[str, list[str]], optional
            Mapping of valid column values.
        data_frame_engine: str, optional
            Dataframe engine to use. Supports 'pandas' and 'polars'.
        drop_columns: list[str], optional
            List of columns to drop.
        strict_validation: bool, optional
            Whether to use strict validation.
        pandas_config: PandasConfig, optional
            Pandas configuration.
        platform_x_mapping: PlatformXMapping, optional
            Platform X mapping.

        Raises
        ------
            InvalidInputError: If the CSV data is invalid.
            ValueError: If the engine is invalid.

        """
        super().__init__()
        self._csv_paths: list[str] = csv_paths
        self._engine: str = data_frame_engine or self._auto_detect_engine()
        self._import_engine_module()
        self.platform_x_mapping: PlatformXMapping = (
            platform_x_mapping or PlatformXMapping()
        )
        self._strict_validation: bool = strict_validation
        if not self._csv_paths:
            self.errors.append(MissingPathsError())
        else:
            self._data_types: list[str] = data_types
            self._unique_value_columns: list[str] = unique_value_columns or []
            self._drop_columns: list[str] = drop_columns or []
            self._column_names: list[str] = column_names
            self._read_columns: list[str] = [
                column_name
                for column_name in self._column_names
                if column_name not in self._drop_columns
            ]
            self._column_schema: dict[str, str] = {
                column_name: self.platform_x_mapping.model_dump()[data_type]
                for column_name, data_type in zip(
                    column_names,
                    data_types,
                    strict=True,
                )
                if "_date" not in column_name.lower() and column_name not in self._drop_columns
            }
            self._date_columns: list[str] = [
                column_name for column_name in self._column_names if "_date" in column_name.lower()
            ]
            if self._engine == "pandas":
                self.data: pd.DataFrame
                self.pandas_config: PandasConfig = pandas_config or PandasConfig()
            elif self._engine == "polars":
                self.lazy_data: pl.LazyFrame
                self._polars_schema: dict[str, pl.DataType] = {}
                self._generate_column_schema_for_polars()
            else:
                message_: str = (
                    f"Invalid engine: {self._engine}. Supported engines are 'pandas' and 'polars'."
                )
                raise ValueError(message_)
            self._columns_with_no_missing_data: list[str] = columns_with_no_missing_data or []
            self._missing_data_column_mapping: dict[str, list[str]] = (
                missing_data_column_mapping or {}
            )
            self._valid_column_values: dict[str, list[str]] = valid_column_values or {}
            self._category_columns: list[str] = [column for column in self._valid_column_values]
            self.__add_category_columns_in_dtype_mapping()
            self.__read()
            if self._engine == "pandas":
                self.number_of_rows: int = len(self.data)
            self.data_columns: set[str] = (
                set(self.data.columns.tolist())
                if self._engine == "pandas"
                else set(self.lazy_data.collect_schema().names())
            )
            self.__analyse()
            if self._engine == "polars":
                self.data = self.lazy_data.collect().to_pandas(use_pyarrow_extension_array=True)
        self._generate_error_message()
        if not self.validate() and self._strict_validation:
            raise InvalidInputError(message=self.error_message)

    @staticmethod
    def _auto_detect_engine() -> str:
        """Pick the first available engine, or fail if none.

        Returns
        -------
            str: The name of the engine to use.

        Raises
        ------
            ImportError: If neither pandas nor polars is installed.

        """
        if _HAS_POLARS:
            return "polars"
        if _HAS_PANDAS:
            return "pandas"
        error_message: str = "You must install either 'pandas' or 'polars' to use CSVValidator."
        raise ImportError(error_message)

    def _import_engine_module(self) -> None:
        """Import pandas or polars on demand and bind to self.pd / self.pl.

        Raises
        ------
            ImportError: If the selected engine is not installed.
            ValueError: If the engine is invalid.

        """
        if self._engine == "pandas":
            try:
                import pandas as pd  # noqa: PLC0415
            except ImportError as e:
                error_ = "Engine 'pandas' was selected, but pandas is not installed."
                raise ImportError(error_) from e
            self.pd = pd

        elif self._engine == "polars":
            try:
                import polars as pl  # noqa: PLC0415
            except ImportError as e:
                error_ = "Engine 'polars' was selected, but polars is not installed."
                raise ImportError(error_) from e
            self.pl = pl

        else:
            error_ = f"Engine {self._engine!r} was selected, but it is not supported."
            raise ValueError(error_)

    def _generate_column_schema_for_polars(self) -> None:
        """Modify the column schema for polars."""
        for column in self._column_schema:
            if self._column_schema[column] == "int":
                self._polars_schema[column] = self.pl.Int64()
            elif self._column_schema[column] == "float":
                self._polars_schema[column] = self.pl.Float64()
            elif self._column_schema[column] == "str":
                self._polars_schema[column] = self.pl.Utf8()
            elif self._column_schema[column] == "category":
                self._polars_schema[column] = self.pl.Categorical()
        self.__add_date_columns_in_polars_schema()

    def __add_category_columns_in_dtype_mapping(self) -> None:
        """Add category columns."""
        for column in self._category_columns:
            self._column_schema[column] = "category"

    def __add_date_columns_in_polars_schema(self) -> None:
        """Add date columns."""
        for column in self._date_columns:
            self._polars_schema[column] = self.pl.Date()

    def __read(self) -> None:
        """Read the CSV data.

        Raises
        ------
            ValueError: If the engine is invalid.

        """

        def _datetime_converter() -> dict[Any, Callable[[str], Any]]:
            """Convert the string column to datetime columns.

            Returns
            -------
                dict[Any, Callable[..., Any]]: Dictionary of date columns.

            """
            return {
                date_column: lambda element: self.pd.to_datetime(
                    arg=element,
                    errors="coerce",
                    format=self.pandas_config.date_format,
                )
                for date_column in self._date_columns
            }

        if self._engine == "pandas":

            def read_file(csv_path: str):  # noqa: ANN202
                if self.pandas_config.pandas_engine == "c":
                    return self.pd.read_csv(
                        filepath_or_buffer=csv_path,
                        engine=self.pandas_config.pandas_engine,
                        dtype=self._column_schema,
                        dtype_backend="pyarrow",
                        date_format=self.pandas_config.date_format,
                        parse_dates=self._date_columns,
                        na_values=self._missing_data_column_mapping,
                        converters=_datetime_converter(),
                        memory_map=True,
                        usecols=self._read_columns,
                    )
                if self.pandas_config.pandas_engine == "pyarrow":
                    return self.pd.read_csv(
                        filepath_or_buffer=csv_path,
                        engine=self.pandas_config.pandas_engine,
                        dtype=self._column_schema,
                        dtype_backend="pyarrow",
                        date_format=self.pandas_config.date_format,
                        parse_dates=self._date_columns,
                        usecols=self._read_columns,
                    )
                error_message: str = f"Invalid pandas engine: {self.pandas_config.pandas_engine}"
                raise ValueError(error_message)

            if len(self._csv_paths) > 1:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    dataframes = list(executor.map(read_file, self._csv_paths))
            else:
                dataframes = [read_file(csv_path=self._csv_paths[0])]

            self.data = self.pd.concat(dataframes, ignore_index=True)
        elif self._engine == "polars":
            self.lazy_data = self.pl.scan_csv(
                source=self._csv_paths,
                try_parse_dates=True,
                rechunk=True,
                infer_schema=True,
            ).drop(self._drop_columns)
        else:
            error_message: str = f"Invalid dataframe engine: {self._engine}"
            raise ValueError(error_message)

    def validate(self) -> bool:
        """Validate the CSV data.

        Returns
        -------
            bool: True if the data is valid, False otherwise.

        """
        return self.errors == []

    def __analyse(self) -> None:
        """Validate the CSV data."""
        if self._date_columns:
            self._check_date_format()
        if self._columns_with_no_missing_data:
            self._check_missing_data()
        if self._valid_column_values:
            self._check_fixed_column_values()
        if self._unique_value_columns:
            self._check_unique_values()

    def validate_keys(self) -> bool | None:
        """Validate keys."""

    def validate_types(self) -> bool | None:
        """Validate types."""

    def validate_values(self) -> bool | None:
        """Validate values."""

    def _check_missing_data(self) -> None:
        """Validate the missing data."""
        if self._engine == "pandas":
            for column in self._columns_with_no_missing_data:
                if column in self.data_columns:
                    missing_mask = self.data[column].isna()
                    if missing_mask.any():
                        error_rows: list[Any] = self.data.index[missing_mask].tolist()
                        self.errors.append(
                            MissingDataError(
                                column=column,
                                rows=error_rows,
                            ),
                        )
                else:
                    self.errors.append(
                        MissingColumnError(
                            column=column,
                        ),
                    )
        elif self._engine == "polars":
            for column in self._columns_with_no_missing_data:
                if column in self.data_columns:
                    missing_df = (
                        self.lazy_data.with_row_index(name="index")
                        .filter(self.pl.col(name=column).is_null())
                        .limit(n=1)
                        .collect()
                    )
                    if missing_df.height > 0:
                        error_rows = missing_df["index"].to_list()
                        self.errors.append(
                            MissingDataError(
                                column=column,
                                rows=error_rows,
                            ),
                        )

    def _check_fixed_column_values(self) -> None:
        """Validate the fixed column values."""
        if self._engine == "pandas":
            for column, valid_values in self._valid_column_values.items():
                self._validate_single_column(column, valid_values)
        elif self._engine == "polars":
            for column, valid_values in self._valid_column_values.items():
                if column in self.data_columns:
                    invalid_rows = (
                        self.lazy_data.filter(~self.pl.col(name=column).is_in(other=valid_values))
                        .limit(1)
                        .collect()
                    )
                    if invalid_rows.height > 0:
                        self.errors.append(
                            FixedValueColumnError(
                                column=column,
                                valid_values=valid_values,
                            ),
                        )
                else:
                    self.errors.append(MissingColumnError(column=column))

    def _validate_single_column(
        self,
        column: str,
        valid_values: list[str],
    ) -> None:
        """Validate a single column.

        Parameters
        ----------
        column: tuple[str, list[str]]
            Tuple of column name and valid values.
        valid_values: list[str]
            List of valid values.

        """
        if column not in self.data_columns:
            self.errors.append(MissingColumnError(column=column))
            return

        if not self.data[column].isin(values=valid_values).all():
            self.errors.append(FixedValueColumnError(column=column, valid_values=valid_values))

    def _check_date_format(self) -> None:
        """Validate that date columns follow the expected ISO8601 format.

        The expected valid dtypes are:
          - datetime64[ns]
          - datetime64[ns, tz]
          - date32[day][pyarrow]
        """
        if self._engine == "pandas":
            valid_dtypes: set[str] = {
                "datetime64[ns]",
                "datetime64[ns, tz]",
                "date32[day][pyarrow]",
            }
            for column in self._date_columns:
                if column in self.data_columns:
                    if self.data[column].dtype.name not in valid_dtypes:
                        self.errors.append(InvalidDateFormatError(column=column))
                else:
                    self.errors.append(MissingColumnError(column=column))
        elif self._engine == "polars":
            schema = self.lazy_data.collect_schema()
            for column in self._date_columns:
                if column in schema:
                    dtype = schema[column]
                    if not dtype.is_temporal():
                        self.errors.append(InvalidDateFormatError(column=column))
                else:
                    self.errors.append(MissingColumnError(column=column))

    def _check_unique_values(self) -> None:
        """Validate the unique values."""
        if self._engine == "pandas":
            for column in self._unique_value_columns:
                if self.data[column].nunique() != self.number_of_rows:
                    self.errors.append(
                        UniqueValueError(column=column),
                    )
        elif self._engine == "polars":
            exprs = [
                self.pl.col(column).n_unique().alias(column)
                for column in self._unique_value_columns
            ]
            exprs.append(self.pl.len().alias("total_rows"))
            result = self.lazy_data.select(exprs).collect()
            total_rows = result["total_rows"][0]
            for column in self._unique_value_columns:
                if result[column][0] != total_rows:
                    self.errors.append(UniqueValueError(column=column))

    def _generate_error_message(self) -> None:
        """Generate error message."""
        self.error_message = "\n".join(
            [f"{index}. {error}" for index, error in enumerate(self.errors, start=1)],
        )

    def _get_integer_columns(self) -> list[str]:
        """Get integer columns.

        Returns
        -------
            list[str]: List of integer columns.

        """
        return self.data.select_dtypes(include="integer").columns.tolist()
