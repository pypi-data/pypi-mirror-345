import pandas as pd
import pytest

from camouflage.adapters import PandasAdapter
from camouflage.registry import _ANONYMIZER_REGISTRY


# Mock anonymizer for test cases
def mock_anonymizer(value):
    return f"anon_{value}"


# Mock deanonymizer for test cases
def mock_deanonymizer(value):
    return value.lstrip("anon_")


@pytest.fixture(autouse=True)
def clear_registry_before_each_test():
    # Clear the registry before each test to avoid interference
    _ANONYMIZER_REGISTRY.clear()


def test_anonymizer_init_with_unregistered_facet():
    # Test initializing PandasAdapter with an unregistered facet
    _ANONYMIZER_REGISTRY["registered_facet"] = mock_anonymizer

    with pytest.raises(
        ValueError,
        match=r"Facet \[unregistered_facet\] is not registered in the anonymizer registry.",
    ):
        PandasAdapter(mapper={"column1": "unregistered_facet"})


def test_anonymizer_init_with_valid_facet():
    _ANONYMIZER_REGISTRY["registered_facet"] = mock_anonymizer

    # Should not raise any exception
    pd_adapter = PandasAdapter(mapper={"column1": "registered_facet"})
    assert isinstance(pd_adapter, PandasAdapter)


def test_anonymize_data_frame():
    _ANONYMIZER_REGISTRY["facet1"] = mock_anonymizer
    pd_adapter = PandasAdapter(mapper={"column1": "facet1"})

    df = pd.DataFrame({"column1": ["value1", "value2", "value3"]})
    df_anonymized = pd_adapter.anonymize(df)

    # Check that anonymized values are applied
    assert df_anonymized["column1"].iloc[0] == "anon_value1"
    assert df_anonymized["column1"].iloc[1] == "anon_value2"
    assert df_anonymized["column1"].iloc[2] == "anon_value3"


def test_deanonymize_data_frame():
    _ANONYMIZER_REGISTRY["facet1"] = mock_anonymizer
    pd_adapter = PandasAdapter(mapper={"column1": "facet1"})

    df = pd.DataFrame({"column1": ["value1", "value2", "value3"]})

    df_anonymized = pd_adapter.anonymize(df)
    df_deanonymized = pd_adapter.deanonymize(df_anonymized)

    # Check that deanonymized values are applied
    assert df_deanonymized["column1"].iloc[0] == "value1"
    assert df_deanonymized["column1"].iloc[1] == "value2"
    assert df_deanonymized["column1"].iloc[2] == "value3"


def test_anonymize_with_multiple_columns():
    _ANONYMIZER_REGISTRY["facet1"] = mock_anonymizer
    _ANONYMIZER_REGISTRY["facet2"] = mock_anonymizer
    pd_adapter = PandasAdapter(mapper={"column1": "facet1", "column2": "facet2"})

    df = pd.DataFrame(
        {
            "column1": ["value1", "value2", "value3"],
            "column2": ["valueA", "valueB", "valueC"],
        }
    )

    df_anonymized = pd_adapter.anonymize(df)

    # Check anonymization for both columns
    assert df_anonymized["column1"].iloc[0] == "anon_value1"
    assert df_anonymized["column2"].iloc[0] == "anon_valueA"


def test_anonymize_empty_dataframe():
    _ANONYMIZER_REGISTRY["facet1"] = mock_anonymizer
    pd_adapter = PandasAdapter(mapper={"column1": "facet1"})

    df_empty = pd.DataFrame({"column1": []})
    df_anonymized = pd_adapter.anonymize(df_empty)

    # Check that the DataFrame remains empty
    assert df_anonymized.empty


def test_deanonymize_with_missing_facet():
    _ANONYMIZER_REGISTRY["facet1"] = mock_deanonymizer
    pd_adapter = PandasAdapter(mapper={"column1": "facet1"})

    df_anonymized = pd.DataFrame(
        {"column1": ["anon_value1", "anon_value2", "anon_value3"]}
    )

    # Test missing facet (because of the absent forward anonymization)
    with pytest.raises(
        ValueError,
        match=r"No facet transform found for facet \[facet1\] in transform \[([0-9a-fA-F-]+)\]",
    ):
        pd_adapter.deanonymize(df_anonymized)
