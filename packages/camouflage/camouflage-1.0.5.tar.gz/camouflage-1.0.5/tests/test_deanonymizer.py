import pytest

from camouflage.deanonymizer import deanonymize
from camouflage.transform import Transform


def test_deanonymize_success():
    transform = Transform()
    transform.add("facet1", "original_value", "anonymized_value")

    result = deanonymize("facet1", "anonymized_value", transform)
    assert result == "original_value"


def test_deanonymize_missing_facet_raises():
    transform = Transform()
    transform.add("facet1", "original_value", "anonymized_value")

    with pytest.raises(
        ValueError, match=r"No facet transform found for facet \[unknown_facet\]"
    ):
        deanonymize("unknown_facet", "anonymized_value", transform)


def test_deanonymize_missing_anonymized_value_raises():
    transform = Transform()
    transform.add("facet1", "original_value", "anonymized_value")

    with pytest.raises(
        ValueError,
        match=r"No original value found for anonymized value \[unknown_value\]",
    ):
        deanonymize("facet1", "unknown_value", transform)


def test_deanonymize_multiple_facets():
    transform = Transform()
    transform.add("facet1", "original_value1", "anonymized_value1")
    transform.add("facet2", "original_value2", "anonymized_value2")

    assert deanonymize("facet1", "anonymized_value1", transform) == "original_value1"
    assert deanonymize("facet2", "anonymized_value2", transform) == "original_value2"
