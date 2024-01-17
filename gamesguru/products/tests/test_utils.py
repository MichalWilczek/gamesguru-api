import re
from gamesguru.products.utils import generate_random_string


def test_generate_random_string():
    result = generate_random_string()

    assert len(result) == 32
    assert bool(re.compile(r'^[a-zA-Z0-9_-]{32}$').match(result))
