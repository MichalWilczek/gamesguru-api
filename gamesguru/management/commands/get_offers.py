import logging
from datetime import datetime, timezone

from django.core.management.base import BaseCommand

from gamesguru.products.schemas import OfferSchemaIn
from gamesguru.products.models import Offer, Product, Shop
from gamesguru.external_apis import get_media_expert_data

_logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Fetches latest playstation data from shops and saves it to the database."

    MEDIA_EXPERT_SHOP_NAME = "MediaExpert"
    PRODUCT_NAME = "Playstation 5"

    def handle(self, *args, **options) -> int:
        now = datetime.now(tz=timezone.utc)

        _logger.info("Fetching data from Media Expert.")
        media_expert_data = get_media_expert_data()
        if media_expert_data:
            shop = Shop.objects.get(name=self.MEDIA_EXPERT_SHOP_NAME)
            product = Product.objects.get(name=self.PRODUCT_NAME)

            products = self._insert_products(
                media_expert_data,
                shop,
                product,
                now
            )
            if products:
                _logger.info(f"Fetched {len(products)} offers from Media Expert to the database.")
        else:
            _logger.warning("No data fetched from Media Expert.")

        return 0

    def _insert_products(self, products: list[OfferSchemaIn], shop: Offer, product: Product, pub_time: datetime):
        objs = []
        for product_data in products:
            data = product_data.dict()
            objs.append(Offer(shop=shop, product=product, pub_time=pub_time, **data))
        return Offer.objects.bulk_create(objs, ignore_conflicts=True)
