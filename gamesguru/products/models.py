import uuid
import urllib.parse

from django.db import models


class Shop(models.Model):
    class Meta:
        verbose_name = "Shop"
        verbose_name_plural = "Shops"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, auto_created=True)
    name = models.CharField(max_length=100)
    tracking_url = models.TextField(max_length=1000, default=None, blank=True)


class Product(models.Model):
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, auto_created=True)
    name = models.CharField(max_length=100)
    epi = models.CharField(max_length=36, default=uuid.uuid4, auto_created=True)


class Offer(models.Model):
    class Meta:
        verbose_name = "Offer"
        verbose_name_plural = "Offers"
        constraints = [
            models.UniqueConstraint(fields=["url"], name="unique_url")
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, auto_created=True)
    name = models.TextField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=20)
    url = models.TextField(max_length=1000)
    pub_time = models.DateTimeField("Publication time")
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    @property
    def affiliation_url(self):
        encoded_base_url = urllib.parse.quote(self.url, safe='')
        return f"{self.shop.tracking_url}&epi={self.product.epi}&url={encoded_base_url}"
