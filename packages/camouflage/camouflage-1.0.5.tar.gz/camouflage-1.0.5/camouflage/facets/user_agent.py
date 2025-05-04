from faker import Faker

from ..registry import register_anonymizer
from ..utils import extract_module_name

module_name = extract_module_name(__file__)

faker = Faker()


def generator_fn(_) -> str:
    """Generates a random user agent string.

    Returns:
        str: The anonymized user agent string.

    """
    return faker.user_agent()


register_anonymizer(module_name, lambda _: faker.user_agent())
