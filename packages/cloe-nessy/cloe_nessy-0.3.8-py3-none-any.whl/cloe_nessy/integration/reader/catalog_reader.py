from typing import Any

from pyspark.sql import DataFrame
from pyspark.sql.utils import AnalysisException

from .exceptions import ReadOperationFailedError
from .reader import BaseReader


class CatalogReader(BaseReader):
    """A reader for Unity Catalog objects.

    This class reads data from a Unity Catalog table and loads it into a Spark DataFrame.
    """

    def __init__(self):
        """Initializes the CatalogReader object."""
        super().__init__()

    def read(self, table_identifier: str = "", **kwargs: Any) -> DataFrame:
        """Reads a table from the Unity Catalog.

        Args:
            table_identifier: The table identifier in the Unity Catalog in the format 'catalog.schema.table'.
            **kwargs: This method does not accept any additional keyword arguments.

        Returns:
            The Spark DataFrame containing the read data.

        Raises:
            ValueError: If the table_identifier is not provided, is not a string, or is not in the correct format.
            Exception: For any other unexpected errors.
        """
        if not table_identifier:
            raise ValueError("table_identifier is required")
        if not isinstance(table_identifier, str):
            raise ValueError("table_identifier must be a string")
        if len(table_identifier.split(".")) != 3:
            raise ValueError("table_identifier must be in the format 'catalog.schema.table'")

        try:
            df = self._spark.read.table(table_identifier)
            return df
        except AnalysisException as err:
            raise ValueError(f"Table not found: {table_identifier}") from err
        except Exception as err:
            raise ReadOperationFailedError(
                f"An error occurred while reading the table '{table_identifier}': {err}"
            ) from err
