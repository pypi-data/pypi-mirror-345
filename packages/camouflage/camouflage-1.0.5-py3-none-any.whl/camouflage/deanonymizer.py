from typing import Any

from .transform import Transform


def deanonymize(facet: str, anonymized_value: Any, transform: Transform) -> Any:
    """Deanonymizes a given value based on the specified facet and transform.

    Args:
        facet (str): The facet for which the value is being deanonymized.
        anonymized_value (Any): The anonymized value to be deanonymized.
        transform (Transform): The transform to be used for deanonymization.

    Returns:
        Any: The deanonymized value.

    """
    return transform.get_backward(facet, anonymized_value)
