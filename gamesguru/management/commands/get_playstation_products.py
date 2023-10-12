import logging
from datetime import datetime, timezone

from django.core.management.base import BaseCommand

from gamesguru.schemas import ElementData
from gamesguru.products.models import Product, Shop
from gamesguru.external_apis import get_media_expert_data

_logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Fetches latest playstation data from shops and saves it to the database."

    MEDIA_EXPERT_SHOP_NAME = "Media Expert"

    def handle(self, *args, **options) -> int:
        now = datetime.now(tz=timezone.utc)

        _logger.info("Fetching data from Media Expert.")
        media_expert_data = get_media_expert_data()
        if media_expert_data:
            shop, _ = Shop.objects.get_or_create(name=self.MEDIA_EXPERT_SHOP_NAME)
            products = self._insert_products(
                media_expert_data,
                shop,
                now
            )
            if products:
                _logger.info(f"{len(products)} Media Expert product(s) added to the database.")
        else:
            _logger.warning("No data fetched from Media Expert.")

        return 0

    def _insert_products(self, products: list[ElementData], shop: Product, pub_time: datetime):
        objs = []
        for product_data in products:
            data = product_data.dict()
            objs.append(Product(shop=shop, pub_time=pub_time, **data))
        return Product.objects.bulk_create(objs)
