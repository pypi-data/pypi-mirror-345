from uuid import UUID

import pytest

from camouflage.transform import FacetTransform, Transform


def test_facet_transform_add_and_retrieve():
    ft = FacetTransform()
    ft.add("original", "anonymized")

    # Forward lookup
    assert ft.get_forward("original") == "anonymized"
    # Backward lookup
    assert ft.get_backward("anonymized") == "original"


def test_facet_transform_missing_forward_raises():
    ft = FacetTransform()

    with pytest.raises(
        ValueError, match=r"No anonymized value found for original value \[missing\]"
    ):
        ft.get_forward("missing")


def test_facet_transform_missing_backward_raises():
    ft = FacetTransform()

    with pytest.raises(
        ValueError, match=r"No original value found for anonymized value \[missing\]"
    ):
        ft.get_backward("missing")


def test_transform_add_and_retrieve_forward_and_backward():
    transform = Transform()
    transform.add("facet1", "original_value", "anonymized_value")

    # Check forward mapping
    assert transform.get_forward("facet1", "original_value") == "anonymized_value"
    # Check backward mapping
    assert transform.get_backward("facet1", "anonymized_value") == "original_value"


def test_transform_forward_missing_facet_raises():
    transform = Transform()

    with pytest.raises(
        ValueError, match=r"No facet transform found for facet \[unknown_facet\]"
    ):
        transform.get_forward("unknown_facet", "some_value")


def test_transform_backward_missing_facet_raises():
    transform = Transform()

    with pytest.raises(
        ValueError, match=r"No facet transform found for facet \[unknown_facet\]"
    ):
        transform.get_backward("unknown_facet", "some_value")


def test_transform_contains_original_and_anonymized():
    transform = Transform()
    transform.add("facet1", "original_value", "anonymized_value")

    # Should find the original and anonymized values
    assert transform.contains_original("facet1", "original_value") is True
    assert transform.contains_anonymized("facet1", "anonymized_value") is True

    # Should not find missing values
    assert transform.contains_original("facet1", "nonexistent") is False
    assert transform.contains_anonymized("facet1", "nonexistent") is False


def test_transform_contains_on_missing_facet():
    transform = Transform()

    # Should return False if facet does not exist
    assert transform.contains_original("missing_facet", "some_value") is False
    assert transform.contains_anonymized("missing_facet", "some_value") is False


def test_transform_uuid_is_valid():
    transform = Transform()
    assert isinstance(transform.uuid, UUID)


def test_multiple_facets_handled_independently():
    transform = Transform()
    transform.add("facet1", "original1", "anonymized1")
    transform.add("facet2", "original2", "anonymized2")

    # Check that facet1 and facet2 don't interfere
    assert transform.get_forward("facet1", "original1") == "anonymized1"
    assert transform.get_forward("facet2", "original2") == "anonymized2"
    assert transform.get_backward("facet1", "anonymized1") == "original1"
    assert transform.get_backward("facet2", "anonymized2") == "original2"


def test_different_transforms_same_facet_independent():
    transform1 = Transform()
    transform2 = Transform()

    transform1.add("shared_facet", "original1", "anonymized1")
    transform2.add("shared_facet", "original2", "anonymized2")

    # transform1 should only know about original1 -> anonymized1
    assert transform1.get_forward("shared_facet", "original1") == "anonymized1"
    with pytest.raises(
        ValueError, match=r"No anonymized value found for original value \[original2\]"
    ):
        transform1.get_forward("shared_facet", "original2")

    # transform2 should only know about original2 -> anonymized2
    assert transform2.get_forward("shared_facet", "original2") == "anonymized2"
    with pytest.raises(
        ValueError, match=r"No anonymized value found for original value \[original1\]"
    ):
        transform2.get_forward("shared_facet", "original1")
