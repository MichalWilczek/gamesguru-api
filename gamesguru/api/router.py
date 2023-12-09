from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.db.models import F, Q
from ninja import Router, Schema

from gamesguru.products.models import Offer, OfferState
from gamesguru.products.schemas import OfferSchemaOut


router = Router()


class Error(Schema):
    msg: str


@router.get("/healthz")
async def healthz(request):
    return {"message": "ok"}


@router.get("/offers", response={
    200: list[OfferSchemaOut],
    500: Error
})
def offers(
        request,
        name: str,
        timedelta_days: int = settings.OFFERS_TIMEDELTA_DAYS,
        max_offers_no: int = settings.MAX_OFFERS_NO
):
    query = Q(
        product__name__iexact=name,
        state__in=[OfferState.VALID, OfferState.NOT_CHECKED],
        pub_time__gte=datetime.now(timezone.utc) - timedelta(days=timedelta_days)
    )

    # Check if user agent comes from a smartphone
    user_agent = request.headers.get('User-Agent')
    if any(header in user_agent.lower() for header in ['iphone', 'android']):
        query = query & Q(shop__show_on_smartphones=True)

    try:
        offers = Offer.objects.filter(
            query).order_by("price")[:max_offers_no].select_related('shop').annotate(shop_name=F('shop__name'))
    except BaseException as e:
        return 500, {"msg": f"Unexpected error occured. Error: {e}"}
    return 200, offers
