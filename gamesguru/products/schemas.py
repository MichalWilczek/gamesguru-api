from ninja import ModelSchema

from gamesguru.products.models import Shop, Product


class ShopSchemaFull(ModelSchema):
    class Config:
        model = Shop
        model_fields = ["id", "name", "tracking_url"]


class ShopSchemaProduct(ModelSchema):
    class Config:
        model = Shop
        model_fields = ["id", "name"]


class ProductSchemaIn(ModelSchema):
    class Config:
        model = Product
        model_fields = ["name", "price", "currency", "url", "affiliation_url"]
        model_fields_optional = ["affiliation_url"]


class ProductSchemaOut(ModelSchema):
    shop: ShopSchemaProduct

    class Config:
        model = Product
        model_fields = ["name", "price", "currency", "affiliation_url", "shop"]
