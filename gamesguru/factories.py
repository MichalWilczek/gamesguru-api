import factory

from gamesguru.products.models import Shop, Product


class ShopFactory(factory.Factory):
    class Meta:
        model = Shop

    name = 'NeoNet'
    tracking_url = 'https://affiliation-url'


class ProductFactory(factory.Factory):
    class Meta:
        model = Product

    name = 'PlayStation 5 z Napędem'
    base_name = 'playstation'
    search_name = 'konsola playstation 5'
    search_words_any_to_exclude = 'digital,slim,chassis'
    search_words_any_to_include = ''
    search_words_all_to_include = ', 5 ,'
    price_lower_limit = 2000
