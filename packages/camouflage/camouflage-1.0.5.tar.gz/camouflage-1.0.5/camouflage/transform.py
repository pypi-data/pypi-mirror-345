from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4


@dataclass
class FacetTransform:
    """Holds the transform between original and anonymized values for a single facet.

    It maintains a forward transform (original to anonymized) and a backward
    transform (anonymized to original) for easy retrieval of values.

    Attributes:
        forward (dict): A dictionary mapping original values to anonymized values.
        backward (dict): A dictionary mapping anonymized values to original values.

    """

    forward: dict = field(default_factory=dict)
    backward: dict = field(default_factory=dict)

    def add(self, original_value: Any, anonymized_value: Any) -> None:
        """Adds a transform between original and anonymized values.

        Args:
            original_value (Any): The original value to be anonymized.
            anonymized_value (Any): The anonymized value corresponding to the original value.

        Returns:
            None: This method does not return anything.

        """
        self.forward[original_value] = anonymized_value
        self.backward[anonymized_value] = original_value

    def get_forward(self, original_value: Any) -> Any:
        """Retrieves the anonymized value for a given original value.

        Args:
            original_value (Any): The original value to be anonymized.

        Returns:
            Any: The anonymized value corresponding to the original value.

        Raises:
            ValueError: If the original value is not found in the forward mapping.

        """
        if original_value not in self.forward:
            raise ValueError(
                f"No anonymized value found for original value [{original_value}]"
            )

        return self.forward[original_value]

    def get_backward(self, anonymized_value: Any) -> Any:
        """Retrieves the original value for a given anonymized value.

        Args:
            anonymized_value (Any): The anonymized value to be de-anonymized.

        Returns:
            Any: The original value corresponding to the anonymized value.

        Raises:
            ValueError: If the anonymized value is not found in the backward mapping.

        """
        if anonymized_value not in self.backward:
            raise ValueError(
                f"No original value found for anonymized value [{anonymized_value}]"
            )

        return self.backward[anonymized_value]


@dataclass
class Transform:
    uuid: UUID = field(default_factory=uuid4)
    facet_transforms: dict[str, FacetTransform] = field(default_factory=dict)

    def add(self, facet: str, original_value: Any, anonymized_value: Any) -> None:
        """Adds a transform between original and anonymized values for a specific facet.

        This method creates a new facet transform if it doesn't already exist.

        Args:
            facet (str): The facet to which the transform belongs.
            original_value (Any): The original value to be anonymized.
            anonymized_value (Any): The anonymized value corresponding to the original value.

        Returns:
            None: This method does not return anything.

        """
        if facet not in self.facet_transforms:
            self.facet_transforms[facet] = FacetTransform()

        self.facet_transforms[facet].add(original_value, anonymized_value)

    def get_forward(self, facet: str, original_value: Any) -> Any:
        """Retrieve the anonymized value for a given original value for a specific facet.

        Args:
            facet (str): The facet to retrieve the anonymized value for.
            original_value (Any): The original value to be anonymized.

        Returns:
            Any: The anonymized value corresponding to the original value.

        Raises:
            ValueError: If the facet is not found in the transform.

        """
        if facet not in self.facet_transforms:
            raise ValueError(
                f"No facet transform found for facet [{facet}] in transform [{self.uuid}]"
            )

        return self.facet_transforms[facet].get_forward(original_value)

    def get_backward(self, facet: str, anonymized_value: Any) -> Any:
        """Retrieve the original value for a given anonymized value for a specific facet.

        Args:
            facet (str): The facet to retrieve the original value for.
            anonymized_value (Any): The anonymized value to be deanonymized.

        Returns:
            Any: The original value corresponding to the anonymized value.

        Raises:
            ValueError: If the facet is not found in the transform.

        """
        if facet not in self.facet_transforms:
            raise ValueError(
                f"No facet transform found for facet [{facet}] in transform [{self.uuid}]"
            )

        return self.facet_transforms[facet].get_backward(anonymized_value)

    def contains_original(self, facet: str, original_value: Any) -> bool:
        """Checks if the original value exists in the forward mapping for the given facet.

        Args:
            facet (str): The facet to check.
            original_value (Any): The original value to check.

        Returns:
            bool: True if the original value exists in the forward mapping, False otherwise.

        """
        if facet not in self.facet_transforms:
            return False

        return original_value in self.facet_transforms[facet].forward

    def contains_anonymized(self, facet: str, anonymized_value: Any) -> bool:
        """Checks if the anonymized value exists in the backward mapping for the given facet.

        Args:
            facet (str): The facet to check.
            anonymized_value (Any): The anonymized value to check.

        Returns:
            bool: True if the anonymized value exists in the backward mapping, False otherwise.

        """
        if facet not in self.facet_transforms:
            return False

        return anonymized_value in self.facet_transforms[facet].backward
