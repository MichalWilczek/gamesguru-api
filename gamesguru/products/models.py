import re
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

    def __str__(self):
        return f"{self.name}"


class Product(models.Model):
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        constraints = [
            models.UniqueConstraint(fields=["name"], name="unique_name"),
            models.UniqueConstraint(fields=["search_name"], name="unique_search_name")
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, auto_created=True)
    name = models.CharField(max_length=100)
    base_name = models.CharField(max_length=100, default=str(name))
    search_name = models.CharField(max_length=100, default=str(name))
    search_words_to_exclude = models.TextField(max_length=1000, blank=True)
    search_words_to_include = models.TextField(max_length=1000, blank=True)
    epi = models.CharField(max_length=36, default=uuid.uuid4, auto_created=True)
    price_lower_limit = models.FloatField(null=True, blank=True)  # applied to avoid scam offers

    @property
    def search_words_to_exclude_list(self) -> list[str]:
        elements = re.split(r',', str(self.search_words_to_exclude))
        return [element for element in elements if element]

    @property
    def search_words_to_include_list(self) -> list[str]:
        elements = re.split(r',', str(self.search_words_to_include))
        return [element for element in elements if element]

    def __str__(self):
        return f"{self.name}"


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
