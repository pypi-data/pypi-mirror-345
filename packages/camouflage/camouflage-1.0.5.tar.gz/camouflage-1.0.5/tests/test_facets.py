import random
from datetime import datetime, timedelta

from camouflage.facets.age import generator_fn as age_generator_fn
from camouflage.facets.amount import generator_fn as amount_generator_fn
from camouflage.facets.country import generator_fn as country_generator_fn
from camouflage.facets.datetime import generator_fn as datetime_generator_fn
from camouflage.facets.ipv4 import generator_fn as ipv4_generator_fn
from camouflage.facets.user_agent import generator_fn as user_agent_generator_fn

RUNS = 1000  # Number of runs for the tests


def test_generator_fn_age():
    min_age = 1
    max_age = 100

    for _ in range(RUNS):
        age = random.randint(min_age, max_age)
        result = age_generator_fn(age)

        assert isinstance(result, int)
        assert 0 <= result <= max_age + 10


def test_generator_fn_amount():
    for _ in range(RUNS):
        amount = random.uniform(1.0, 1000.0)
        result = amount_generator_fn(amount)

        assert isinstance(result, float)
        assert 0.5 * amount <= result <= 1.5 * amount


def test_generator_fn_country():
    for _ in range(RUNS):
        result = country_generator_fn(_)

        assert isinstance(result, str)
        assert len(result) > 0


def test_generator_fn_date():
    for _ in range(RUNS):
        test_date = datetime(2025, 1, 1)
        result = datetime_generator_fn(test_date)

        assert isinstance(result, datetime)
        assert result > test_date
        assert result - test_date <= timedelta(days=1000)


def test_generator_fn_ipv4():
    for _ in range(RUNS):
        result = ipv4_generator_fn(_)

        assert isinstance(result, str)

        parts = result.split(".")
        assert len(parts) == 4
        assert all(part.isdigit() for part in parts)
        assert all(0 <= int(part) <= 255 for part in parts)


def test_generator_fn_user_agent():
    for _ in range(RUNS):
        result = user_agent_generator_fn(_)

        assert isinstance(result, str)
        assert len(result) > 0
