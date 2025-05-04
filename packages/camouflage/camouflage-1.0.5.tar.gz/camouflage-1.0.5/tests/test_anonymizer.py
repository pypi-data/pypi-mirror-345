from unittest.mock import Mock

import pytest

from camouflage.anonymizer import anonymize
from camouflage.registry import _ANONYMIZER_REGISTRY
from camouflage.transform import Transform


@pytest.fixture(autouse=True)
def clear_registry_before_each_test():
    _ANONYMIZER_REGISTRY.clear()


def dummy_generator(value):
    return f"anon_{value}"


def collision_generator(value):
    # Always returns same anonymized value to simulate collisions
    return "constant_anon_value"


def test_anonymize_without_transform():
    _ANONYMIZER_REGISTRY["test_facet"] = dummy_generator

    result = anonymize("test_facet", "original_value")
    assert result == "anon_original_value"


def test_anonymize_without_registered_anonymizer_raises():
    with pytest.raises(
        ValueError, match=r"No anonymizer registered for facet \[unknown_facet\]"
    ):
        anonymize("unknown_facet", "original_value")


def test_anonymize_with_transform_new_value():
    _ANONYMIZER_REGISTRY["test_facet"] = dummy_generator
    transform = Transform()

    anonymized = anonymize("test_facet", "original_value", transform)

    # Should generate and store the mapping
    assert anonymized == "anon_original_value"
    assert (
        transform.get_forward("test_facet", "original_value") == "anon_original_value"
    )
    assert (
        transform.get_backward("test_facet", "anon_original_value") == "original_value"
    )


def test_anonymize_with_transform_existing_value():
    mock_generator = Mock(side_effect=lambda value: f"anon_{value}")
    _ANONYMIZER_REGISTRY["test_facet"] = mock_generator
    transform = Transform()
    transform.add("test_facet", "original_value", "already_anonymized")

    # Call anonymize with a pre-existing mapping
    anonymized = anonymize("test_facet", "original_value", transform)

    # Assert the existing mapping is returned
    assert anonymized == "already_anonymized"

    # Assert the generator was not called
    mock_generator.assert_not_called()


def test_anonymize_with_transform_and_collision_handling():
    _ANONYMIZER_REGISTRY["test_facet"] = collision_generator
    transform = Transform()

    # Pre-fill transform with a conflicting anonymized value
    transform.add("test_facet", "existing_original", "constant_anon_value")

    # Track calls to the generator
    call_count = {"count": 0}

    def non_colliding_generator(value):
        # First call returns collision, second call returns unique
        if call_count["count"] == 0:
            call_count["count"] += 1
            return "constant_anon_value"
        else:
            return "unique_anon_value"

    mock_generator = Mock(side_effect=non_colliding_generator)
    _ANONYMIZER_REGISTRY["test_facet"] = mock_generator

    anonymized = anonymize("test_facet", "new_original", transform)

    assert anonymized == "unique_anon_value"
    assert transform.get_forward("test_facet", "new_original") == "unique_anon_value"
    assert transform.get_backward("test_facet", "unique_anon_value") == "new_original"

    # Assert the generator was called twice
    assert mock_generator.call_count == 2
