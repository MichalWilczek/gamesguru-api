import logging
from datetime import datetime, timezone

from django.core.management.base import BaseCommand

from gamesguru.products.schemas import OfferSchemaIn
from gamesguru.products.models import Offer, Product, Shop
from gamesguru.products.offers_scraping import run_scraping

_logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Fetches latest offers from multiple shops and saves them to the database."

    def handle(self, *args, **options) -> int:
        now = datetime.now(tz=timezone.utc)

        shops = list(Shop.objects.all())
        products = list(Product.objects.all())
        offers = []
        for shop in shops:
            for product in products:
                scraped_offers = run_scraping(shop, product)
                processed_offers = self._filter_out_scam_offers(
                    self._to_model_offers(scraped_offers, shop, product, now)
                )
                offers.extend(processed_offers)
                _logger.info(f"Shop: {shop.name}. Product: {product.name}. "
                             f"Scraped {len(scraped_offers)} offers. Accepted: {len(processed_offers)}.")

                try:
                    db_result = Offer.objects.bulk_create(
                        processed_offers,
                        update_conflicts=True,
                        update_fields=["name", "price", "currency", "url", "pub_time", "shop", "product"],
                        unique_fields=['url']
                    )
                    if (not db_result) and len(processed_offers) > 0:
                        _logger.warning(f"Shop: {shop.name}. No data saved to the database.")
                except BaseException as e:
                    _logger.error(f"Unexpected error occurred: {e}")

        return 0

    def _filter_out_scam_offers(self, offers: list[Offer]):
        filtered_offers = []
        urls = []
        for offer in offers:
            product = offer.product
            if product.price_lower_limit and offer.price < product.price_lower_limit:
                continue
            if offer.url in urls:
                continue
            else:
                urls.append(offer.url)
            filtered_offers.append(offer)
        return filtered_offers

    def _to_model_offers(
            self, offers: list[OfferSchemaIn], shop: Offer, product: Product, pub_time: datetime) -> list[Offer]:
        objs = []
        for offer in offers:
            data = offer.dict()
            objs.append(Offer(shop=shop, product=product, pub_time=pub_time, **data))
        return objs
