import os
import pytest
from pytest_factoryboy import register

from gamesguru.factories import (
    ShopFactory,
    ProductFactory
)

register(ShopFactory)
register(ProductFactory)


@pytest.fixture(autouse=True)
def run_before_tests():
    os.environ['ENV'] = 'test'
