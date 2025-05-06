"""CSV configuration rules."""


from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings


class PlatformXMapping(BaseModel):
    """Platform-X data type mapping."""

    model_config = ConfigDict(
        strict=False,
        extra="allow",
    )

    integer: str = "int"
    varchar: str = "str"
    character: str = "str"
    numeric: str = "float"
    double: str = "float"
    integer64: str = "int"
    int: str = "int"


class PandasConfig(BaseSettings):
    """Pandas configuration rules."""

    def __init__(
        self,
        pandas_engine: str = "pyarrow",
        date_format: str = "ISO8601",
        max_rows_to_display: int = 10,
        max_columns_to_display: int = 50,
    ) -> None:
        """Initialize the PandasConfig class."""
        super().__init__()
        self.pandas_engine: str = pandas_engine
        self.date_format: str = date_format
        self.pandas_dtype_mapping: PlatformXMapping = Field(
            default_factory=PlatformXMapping,
            alias="PANDAS_DTYPE_MAPPING",
        )
        self.max_rows: int = max_rows_to_display
        self.max_columns: int = max_columns_to_display
