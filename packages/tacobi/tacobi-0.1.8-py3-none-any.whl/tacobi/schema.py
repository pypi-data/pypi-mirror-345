from datetime import timedelta
from enum import Enum
from typing import Callable, Iterable, Type, TypeVar

from pandera.typing.common import DataFrameBase
from pydantic import BaseModel, Field, computed_field, field_validator

from tacobi.pandera import pa
from tacobi.type_utils import extract_model_from_typehints
from tacobi.value_types import ValueTypeEnum

DataFrameBaseT = TypeVar("DataFrameBaseT", bound=DataFrameBase)
DatasetFunctionType = Callable[[], DataFrameBaseT]

# Dataset Type ---------------------------------------------------------------


class DatasetTypeEnum(str, Enum):
    TABULAR = "tabular"


# Dataset Schemas


class DatasetSchema(BaseModel):
    @classmethod
    def from_dataframe_model(
        cls, dataframe_model: Type[pa.DataFrameModel]
    ) -> "DatasetSchema":
        raise NotImplementedError


# Tabular Dataset Schema -----------------------------------------------------


class TabularDatasetColumnSchema(BaseModel):
    name: str
    valueType: ValueTypeEnum


class TabularDatasetSchema(DatasetSchema):
    columns: list[TabularDatasetColumnSchema]

    @classmethod
    def from_dataframe_model(
        cls, dataframe_model: Type[pa.DataFrameModel]
    ) -> "TabularDatasetSchema":
        schema_columns: Iterable[pa.Column] = (
            dataframe_model.to_schema().columns.values()
        )

        return cls(
            columns=[
                TabularDatasetColumnSchema(
                    name=col.name,
                    valueType=ValueTypeEnum.from_pandera_dtype(col.dtype),
                )
                for col in schema_columns
            ]
        )


# DatasetSchema Type ----------------------------------------------------------------

DatasetSchemaT = TabularDatasetSchema

# Dataset ---------------------------------------------------------------------


class Dataset(BaseModel):
    id: str
    route: str
    type: DatasetTypeEnum
    function: DatasetFunctionType = Field(exclude=True)
    cache_validity: timedelta | None = Field(exclude=True, default=None)

    @field_validator("cache_validity")
    def validate_cache_validity(cls, v: timedelta | None) -> timedelta | None:
        """Validate that cache_validity is a positive timedelta if provided."""
        if v is not None and v.total_seconds() <= 0:
            raise ValueError("cache_validity must be a positive timedelta")
        return v

    @property
    def dataframe_model(self) -> Type[pa.DataFrameModel]:
        """
        Extract the DataFrameModel from a function that returns DataFrame[DataFrameModel].

        This property inspects the return type annotation of the function and extracts
        the DataFrameModel from it.

        Returns:
            Type[pa.DataFrameModel]: The DataFrameModel class used in the DataFrame type annotation

        Raises:
            TypeError: If the function's return type is not properly annotated with DataFrame[DataFrameModel]
        """
        return extract_model_from_typehints(
            func=self.function,
            expected_container_type=DataFrameBase,
            expected_model_base=pa.DataFrameModel,
        )

    @computed_field
    def dataset_schema(self) -> DatasetSchemaT:
        match self.type:
            case DatasetTypeEnum.TABULAR:
                return TabularDatasetSchema.from_dataframe_model(self.dataframe_model)
            case _:
                raise ValueError(f"Unsupported dataset type: {self.type}")


# Schema ----------------------------------------------------------------------


class Schema(BaseModel):
    datasets: list[Dataset]
