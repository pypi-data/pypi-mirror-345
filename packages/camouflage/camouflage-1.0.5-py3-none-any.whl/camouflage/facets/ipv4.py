from faker import Faker

from ..registry import register_anonymizer
from ..utils import extract_module_name

module_name = extract_module_name(__file__)

faker = Faker()


def generator_fn(_) -> str:
    """Generates a random IP address.

    Returns:
        str: The anonymized IP address.

    """
    return faker.ipv4()


register_anonymizer(module_name, generator_fn)
