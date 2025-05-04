import random
from datetime import datetime, timedelta

from ..registry import register_anonymizer
from ..utils import extract_module_name

module_name = extract_module_name(__file__)


def generator_fn(dt: datetime) -> datetime:
    """Generates a random date based on the original date.

    Args:
        dt (datetime): The original date.

    Returns:
        datetime: The anonymized date.

    """
    return dt + timedelta(days=random.randint(1, 1_000))


register_anonymizer(module_name, generator_fn)
