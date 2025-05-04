from datetime import timedelta
from functools import wraps
from typing import Callable, TypeVar

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pandera.typing.common import DataFrameBase

from tacobi.caching import CacheAdapter, DiskCacheAdapter
from tacobi.pandera import pa
from tacobi.schema import Dataset, DatasetTypeEnum, Schema
from tacobi.type_utils import (
    extract_container_type,
    extract_model_from_typehints,
    extract_return_type,
)

DataFrameBaseT = TypeVar("DataFrameBaseT", bound=DataFrameBase)
DatasetFunctionType = Callable[[], DataFrameBaseT]


class Tacobi:
    def __init__(
        self,
        fastapi_app: FastAPI | None = None,
        cache_adapter: CacheAdapter | None = None,
    ):
        self._fastapi_app = fastapi_app if fastapi_app is not None else FastAPI()
        self._fastapi_app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allows all origins
            allow_credentials=True,
            allow_methods=["*"],  # Allows all methods
            allow_headers=["*"],  # Allows all headers
        )
        self._datasets: list[Dataset] = []
        self._cache_adapter = (
            cache_adapter if cache_adapter is not None else DiskCacheAdapter()
        )

    def _attach_type_check_to_func(
        self, func: DatasetFunctionType
    ) -> DatasetFunctionType:
        """Attach pandera typechecking to a function.

        This is a simple wrapper around pandera's check_types function.
        This is implemented in a separate function mainly to prevent mypy from complaining.

        Args:
            func: The function to attach the typechecking to.

        Returns:
            The function with the typechecking attached.
        """
        return pa.check_types(func)

    def _attach_cache_to_function(
        self, func: DatasetFunctionType, cache_validity: timedelta
    ) -> DatasetFunctionType:
        @wraps(func)
        def cached_func():
            cache_key = func.__name__
            cached_value = self._cache_adapter.get(cache_key)
            if cached_value is not None:
                return cached_value
            else:
                value = func()
                self._cache_adapter.set(
                    cache_key, value, cache_validity.total_seconds()
                )
                return value

        return cached_func

    def _attach_dataset_to_fastapi(self, dataset: Dataset):
        """Attach a dataset to a FastAPI route.

        We infer the return model from the function's return type.
        We alter the return model to be serializable by fastapi.

        Args:
            dataset: The dataset to attach to the FastAPI route.
        """
        return_type = extract_return_type(dataset.function)
        container_type = extract_container_type(return_type, DataFrameBase)
        model = extract_model_from_typehints(
            dataset.function, container_type, pa.DataFrameModel
        )

        class FastApiModel(model):  # type: ignore
            class Config(model.Config):  # type: ignore
                to_format = "dict"
                to_format_kwargs = {"orient": "records"}

        self._fastapi_app.get(
            dataset.route, response_model=container_type[FastApiModel]
        )(dataset.function)

    def dataset(
        self,
        route: str,
        dataset_type: DatasetTypeEnum,
        cache_validity: timedelta | None = None,
    ) -> Callable[[DatasetFunctionType], DatasetFunctionType]:
        """Decorator to define a dataset.

        This decorator also attaches typechecking functionality to the function and properly registers
        it with the FastAPI app.

        Args:
            route: The route at which the dataset can be accessed from the api.
            dataset_type: The type of dataset.
            cache_validity: The validity of the cache for the dataset. If none, caching is disabled.

        Returns:
            The decorated function.
        """

        def decorator(func: DatasetFunctionType) -> DatasetFunctionType:
            func = self._attach_type_check_to_func(func)

            if cache_validity is not None:
                func = self._attach_cache_to_function(func, cache_validity)

            dataset = Dataset(
                id=func.__name__,
                route=route,
                type=dataset_type,
                function=func,
                cache_validity=cache_validity,
            )

            self._datasets.append(dataset)

            self._attach_dataset_to_fastapi(dataset)

            return func

        return decorator

    def get_schema(self) -> Schema:
        return Schema(datasets=self._datasets)

    def run(self):
        uvicorn.run(self._fastapi_app, host="0.0.0.0", port=8000)
