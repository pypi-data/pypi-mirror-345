import pytest

from camouflage.registry import _ANONYMIZER_REGISTRY, register_anonymizer


def dummy_generator_fn(value):
    return f"anon_{value}"


def another_dummy_generator_fn(value):
    return f"anon2_{value}"


@pytest.fixture(autouse=True)
def clear_registry_before_each_test():
    # Clear the registry before each test to avoid interference
    _ANONYMIZER_REGISTRY.clear()


def test_register_new_anonymizer_successfully():
    register_anonymizer("test_facet", dummy_generator_fn)

    assert "test_facet" in _ANONYMIZER_REGISTRY
    assert _ANONYMIZER_REGISTRY["test_facet"] is dummy_generator_fn


def test_register_duplicate_anonymizer_raises():
    register_anonymizer("test_facet", dummy_generator_fn)

    with pytest.raises(
        ValueError, match=r"Anonymizer for facet \[test_facet\] already registered"
    ):
        register_anonymizer("test_facet", another_dummy_generator_fn)


def test_register_multiple_different_anonymizers():
    register_anonymizer("facet1", dummy_generator_fn)
    register_anonymizer("facet2", another_dummy_generator_fn)

    assert _ANONYMIZER_REGISTRY["facet1"] is dummy_generator_fn
    assert _ANONYMIZER_REGISTRY["facet2"] is another_dummy_generator_fn
    assert len(_ANONYMIZER_REGISTRY) == 2


def test_registered_anonymizer_callable_behavior():
    register_anonymizer("test_facet", dummy_generator_fn)

    result = _ANONYMIZER_REGISTRY["test_facet"]("my_value")
    assert result == "anon_my_value"
