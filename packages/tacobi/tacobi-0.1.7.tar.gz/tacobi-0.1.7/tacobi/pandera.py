from importlib.util import find_spec

__all__ = ["pa"]

if find_spec("polars"):
    import pandera.polars as pa  # type: ignore
elif find_spec("pandas"):
    import pandera as pa  # type: ignore
else:
    raise ImportError("Neither polars nor pandas are installed")
