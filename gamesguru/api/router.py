from datetime import datetime, timedelta, timezone

from django.db.models import F
from ninja import Router, Schema

from gamesguru.products.models import Offer
from gamesguru.products.schemas import OfferSchemaOut


router = Router()


class Error(Schema):
    msg: str


@router.get("/healthz")
def healthz(request):
    return {"message": "ok"}


@router.get("/products", response={
    200: list[OfferSchemaOut],
    204: Error,
    500: Error
})
def products(request):
    now = datetime.now(timezone.utc)
    try:
        objs = Offer.objects.filter(
            name__icontains="playstation 5",
            pub_time__gte=now - timedelta(days=30)
        ).order_by("price")[:5].select_related('shop').annotate(shop_name=F('shop__name'))
        a = list(objs)
    except BaseException as e:
        return 500, {"msg": f"Unexpected error occured. Error: {e}"}
    if len(objs) == 0:
        return 204, {"msg": "No data in the database from the last month."}
    return 200, objs
