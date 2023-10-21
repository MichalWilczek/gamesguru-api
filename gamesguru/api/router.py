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


@router.get("/products", response={
    200: list[OfferSchemaOut],
    204: Error,
    500: Error
})
def products(request):
    try:
        objs = Offer.objects.filter(
            name__icontains="playstation 5",
            pub_time__gte=datetime.now(timezone.utc) - timedelta(days=30)
        ).order_by("price")[:5].select_related('shop').annotate(shop_name=F('shop__name'))
    except BaseException as e:
        return 500, {"msg": f"Unexpected error occured. Error: {e}"}
    if len(objs) == 0:
        return 204, {"msg": "No data in the database from the last 30 days."}
    return 200, objs
