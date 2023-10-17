import logging
from datetime import datetime, timezone
import urllib.parse

from django.core.management.base import BaseCommand

from gamesguru.products.schemas import ProductSchemaIn
from gamesguru.products.models import Product, Shop
from gamesguru.external_apis import get_media_expert_data

_logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Fetches latest playstation data from shops and saves it to the database."

    MEDIA_EXPERT_SHOP_NAME = "MediaExpert (PL)"

    def handle(self, *args, **options) -> int:
        now = datetime.now(tz=timezone.utc)

        _logger.info("Fetching data from Media Expert.")
        media_expert_data = get_media_expert_data()
        if media_expert_data:
            shop, _ = Shop.objects.get_or_create(name=self.MEDIA_EXPERT_SHOP_NAME)

            if shop.tracking_url is not None:
                for elem in media_expert_data:
                    elem.affiliation_url = self._affiliate_url(elem.url, shop.tracking_url)

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

    def _affiliate_url(self, url: str, tracking_link: str) -> str:
        encoded_base_url = urllib.parse.quote(url, safe='')
        return f"{tracking_link}&url={encoded_base_url}"

    def _insert_products(self, products: list[ProductSchemaIn], shop: Product, pub_time: datetime):
        objs = []
        for product_data in products:
            data = product_data.dict()
            objs.append(Product(shop=shop, pub_time=pub_time, **data))
        return Product.objects.bulk_create(objs, ignore_conflicts=True)
