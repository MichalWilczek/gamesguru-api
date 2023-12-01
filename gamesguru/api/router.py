from datetime import datetime, timedelta, timezone

from django.db.models import F
from ninja import Router, Schema

from gamesguru.products.models import Offer
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
        timedelta_days: int = 2,
        max_offers_no: int = 5
):
    try:
        offers = Offer.objects.filter(
            product__name__icontains=name,
            pub_time__gte=datetime.now(timezone.utc) - timedelta(days=timedelta_days)
        ).order_by("price")[:max_offers_no].select_related('shop').annotate(shop_name=F('shop__name'))
    except BaseException as e:
        return 500, {"msg": f"Unexpected error occured. Error: {e}"}
    return 200, offers
