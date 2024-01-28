import pytest

from gamesguru.products.offers_scraping import (
    Empik,
    MediaExpert,
    MediaMarkt,
    NeoNet,
    RTVEuroAGD,
    OleOle
)
from gamesguru.products.offers_scraping import (
    get_metadata
)


@pytest.mark.parametrize(
    'shop_name,expected_shop_obj', [
        ('Empik', Empik),
        ('Media Expert', MediaExpert),
        ('MediaMarkt', MediaMarkt),
        ('Neonet', NeoNet),
        ('OleOle', OleOle),
        ('RTV EURO AGD', RTVEuroAGD),
    ]
)
def test_get_metadata(shop_factory, shop_name, expected_shop_obj):
    shop = shop_factory(name=shop_name)
    assert isinstance(get_metadata(shop), expected_shop_obj)


def test_get_offer_name():
    pass


def test_is_name_valid():
    pass


def test_get_prices():
    pass


def test_remove_ascii_characters():
    pass
