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
    # TODO: This might not be needed (nor working...)
    os.environ['ENV'] = 'test'


# @pytest.fixture
# def product_playstation_5(product_factory):
#     pass
#
#
# @pytest.fixture
# def product_playstation_digital_5(product_factory):
#     return product_factory(
#         name='Playstation 5 Digital',
#         base_name='playstation',
#         search_name='konsola playstation 5 digital',
#         search_words_any_to_exclude='slim,chassis,naped,napęd',
#         search_words_any_to_include='',
#         search_words_all_to_include='digital, 5 ,',
#         price_lower_limit=1500.0
#     )
#
#
# @pytest.fixture
# def product_playstation_slim_5(product_factory):
#     return product_factory(
#         name='Playstation 5 Slim z Napędem',
#         base_name='playstation',
#         search_name='konsola playstation 5 slim',
#         search_words_any_to_exclude='digital',
#         search_words_any_to_include='slim,chassis',
#         search_words_all_to_include=', 5 ,',
#         price_lower_limit=1500.0
#     )
#
#
# @pytest.fixture
# def product_playstation_slim_digital_5(product_factory):
#     pass
