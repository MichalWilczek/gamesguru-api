import uuid

from django.db import models


class Shop(models.Model):
    class Meta:
        verbose_name = "Shop"
        verbose_name_plural = "Shops"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, auto_created=True)
    name = models.CharField(max_length=25)


class Product(models.Model):
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        constraints = [
            models.UniqueConstraint(fields=["url"], name="unique_url")
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, auto_created=True)
    name = models.TextField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.TextField(max_length=10)
    url = models.TextField(max_length=1000)
    pub_time = models.DateTimeField("Publication time")
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
