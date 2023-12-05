import logging
from datetime import datetime, timezone, timedelta

from django.core.management.base import BaseCommand
from django.db.models import F
from django.conf import settings

from gamesguru.products.models import Offer, Product, OfferState
from gamesguru.products.offers_scraping import scrap_offer_for_validity

_logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Checks if the specified offers are still valid."

    def handle(self, *args, **options) -> int:
        now = datetime.now(tz=timezone.utc)
        products = Product.objects.all()

        for product in products:
            offers = Offer.objects.filter(
                product=product,
                state__in=[OfferState.VALID, OfferState.NOT_CHECKED],
                pub_time__gte=now - timedelta(days=settings.OFFERS_TIMEDELTA_DAYS),
            ).order_by("price")[:settings.MAX_OFFERS_NO].select_related(
                'shop').annotate(shop_name=F('shop__name'))

            offers = list(offers)
            valid_offers_no = 0
            outdated_offers_no = 0
            for offer in offers:
                is_valid = scrap_offer_for_validity(offer)
                if is_valid:
                    offer.state = OfferState.VALID
                    valid_offers_no += 1
                else:
                    offer.state = OfferState.OUTDATED
                    outdated_offers_no += 1
                offer.state_check_time = now
                offer.save()
            _logger.info(f"Product: {product.name}. Valid: {valid_offers_no}, outdated: {outdated_offers_no}")
