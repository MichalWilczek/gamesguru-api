from ninja import ModelSchema, Schema

from gamesguru.products.models import Shop, Offer


class ShopSchemaFull(ModelSchema):
    class Config:
        model = Shop
        model_fields = ["id", "name", "tracking_url"]


class ShopSchemaProduct(ModelSchema):
    class Config:
        model = Shop
        model_fields = ["id", "name"]


class OfferSchemaIn(ModelSchema):
    class Config:
        model = Offer
        model_fields = ["name", "price", "currency", "url"]


class OfferSchemaOut(Schema):
    name: str
    price: int
    currency: str
    shop_name: str
    url: str
    affiliation_url: str
