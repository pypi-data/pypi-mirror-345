from faker import Faker

from ..registry import register_anonymizer
from ..utils import extract_module_name

module_name = extract_module_name(__file__)

faker = Faker()


def generator_fn(_) -> str:
    """Generates a random country.

    Returns:
        str: The anonymized country.

    """
    return faker.country()


register_anonymizer(module_name, generator_fn)
