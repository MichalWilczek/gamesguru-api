from ninja import ModelSchema

from gamesguru.products.models import Shop, Product


class ShopSchema(ModelSchema):
    class Config:
        model = Shop
        model_fields = ["id", "name"]


class ProductSchemaIn(ModelSchema):
    class Config:
        model = Product
        model_fields =  ["name", "price", "currency", "url"]


class ProductSchemaOut(ProductSchemaIn):
    shop: ShopSchema

    class Config:
        model_fields = ProductSchemaIn.Config.model_fields + ["id", "shop"]
