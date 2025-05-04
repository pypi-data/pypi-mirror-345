from typing import Any, Callable

_ANONYMIZER_REGISTRY: dict[str, Callable[[Any], Any]] = {}
"""A global registry to hold different anonymizer functions.

This registry allows for the dynamic addition of anonymization functions
for different facets.

The key is the facet (e.g., "email", "phone"), and the value is a
callable function that takes a value of that facet and returns
an anonymized version of that value.

"""


def register_anonymizer(facet: str, generator_fn: Callable[[Any], Any]) -> None:
    """Registers a generator function for a specific facet.

    This allows for the dynamic addition of anonymization functions for
    different facets, enabling the system to handle various data
    anonymization needs.

    The generator function should take a value of the specified facet
    and return an anonymized version of that value.

    Args:
        facet (str): The type of facet for which the generator function is being registered.
        generator_fn (Callable[[Any], Any]): The generator function that will be used for anonymization.

    Returns:
        None: This function does not return anything.

    Raises:
        ValueError: If the facet is already registered in the registry.

    """
    if facet in _ANONYMIZER_REGISTRY:
        raise ValueError(f"Anonymizer for facet [{facet}] already registered")

    _ANONYMIZER_REGISTRY[facet] = generator_fn
