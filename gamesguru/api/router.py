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
    204: Error,
    500: Error
})
def offers(
        request,
        name: str,
        latest_pub_date: datetime = datetime.now(timezone.utc) - timedelta(days=30),
        max_offers_no: int = 5
):
    try:
        objs = Offer.objects.filter(
            name__icontains=name,
            pub_time__gte=latest_pub_date
        ).order_by("price")[:max_offers_no].select_related('shop').annotate(shop_name=F('shop__name'))
    except BaseException as e:
        return 500, {"msg": f"Unexpected error occured. Error: {e}"}
    if len(objs) == 0:
        return 204, {"msg": f"No data in the database from: {latest_pub_date.isoformat()}."}
    return 200, objs
