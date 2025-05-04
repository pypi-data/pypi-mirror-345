import pandas as pd

from .anonymizer import anonymize
from .deanonymizer import deanonymize
from .registry import _ANONYMIZER_REGISTRY
from .transform import Transform


class PandasAdapter:
    """Anonymize and deanonymize data in a pandas DataFrame."""

    def __init__(self, mapper: dict[str, str]) -> None:
        """Validate the mapper and initialize the PandasAdapter.

        Args:
            mapper (dict[str, str]): A dictionary mapping column names to facets.
                Each facet should be registered in the anonymizer registry.

        Returns:
            None: This method does not return anything.

        Raises:
            ValueError: If any facet in the mapper is not registered in the anonymizer registry.

        """
        for facet in mapper.values():
            if facet not in _ANONYMIZER_REGISTRY:
                raise ValueError(
                    f"Facet [{facet}] is not registered in the anonymizer registry."
                )

        self.mapper = mapper
        self.transform = Transform()

    def anonymize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return a new DataFrame with anonymized data.

        Args:
            df (pd.DataFrame): The DataFrame to anonymize.

        Returns:
            pd.DataFrame: A new DataFrame with anonymized data.

        """
        df_anonymized = df.copy()

        for column_name, facet in self.mapper.items():
            anonymize_fn = lambda v, f=facet, t=self.transform: anonymize(f, v, t)
            df_anonymized[column_name] = df_anonymized[column_name].apply(anonymize_fn)

        return df_anonymized

    def deanonymize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return a new DataFrame with deanonymized data.

        Args:
            df (pd.DataFrame): The DataFrame to deanonymize.

        Returns:
            pd.DataFrame: A new DataFrame with deanonymized data.

        """
        df_deanonymized = df.copy()

        for column_name, facet in self.mapper.items():
            deanonymize_fn = lambda v, f=facet, t=self.transform: deanonymize(f, v, t)
            df_deanonymized[column_name] = df_deanonymized[column_name].apply(
                deanonymize_fn
            )

        return df_deanonymized
