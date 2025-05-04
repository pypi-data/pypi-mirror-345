from typing import Any

from .registry import _ANONYMIZER_REGISTRY
from .transform import Transform


def anonymize(
    facet: str, original_value: Any, transform: Transform | None = None
) -> Any:
    """Anonymize a given value based on the specified facet and transform.

    Args:
        facet (str): The facet for which the value is being anonymized.
        original_value (Any): The original value to be anonymized.
        transform (Transform | None): The transform to be used for anonymization.
            If None, a one-time anonymization is performed.

    Returns:
        Any: The anonymized value.

    Raises:
        ValueError: If the facet is not registered in the anonymizer registry.

    """
    if facet not in _ANONYMIZER_REGISTRY:
        raise ValueError(f"No anonymizer registered for facet [{facet}]")

    generator_fn = _ANONYMIZER_REGISTRY[facet]

    if transform is None:
        return generator_fn(original_value)

    if not transform.contains_original(facet, original_value):
        while True:
            anonymized_value = generator_fn(original_value)
            if not transform.contains_anonymized(facet, anonymized_value):
                break

        transform.add(facet, original_value, anonymized_value)

    else:
        anonymized_value = transform.get_forward(facet, original_value)

    return anonymized_value
