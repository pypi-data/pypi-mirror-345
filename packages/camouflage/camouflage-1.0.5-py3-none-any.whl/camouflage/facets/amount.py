import random

from ..registry import register_anonymizer
from ..utils import extract_module_name

module_name = extract_module_name(__file__)


def generator_fn(amount: float) -> float:
    """Generates a random amount based on the original amount.

    Args:
        amount (float): The original amount.

    Returns:
        float: The anonymized amount.

    """
    return round(amount * random.uniform(0.5, 1.5), 2)


register_anonymizer(module_name, generator_fn)
