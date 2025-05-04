from faker import Faker

from ..registry import register_anonymizer
from ..utils import extract_module_name

module_name = extract_module_name(__file__)

faker = Faker()


def generator_fn(_) -> int:
    """Generates a random age.

    Returns:
        int: The anonymized age.

    """
    return faker.random_int(min=0, max=100)


register_anonymizer(module_name, generator_fn)
