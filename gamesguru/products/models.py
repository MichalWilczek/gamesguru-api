import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy
from django.utils import timezone

from .affiliations import Tradedoubler, Convertiser
from .utils import generate_random_string


class Affiliation(models.TextChoices):
    """List of available affiliation generators"""
    TRADEDOUBLER = 'tradedoubler', gettext_lazy('Tradedoubler')
    CONVERTISER = 'convertiser', gettext_lazy('Convertiser')


class Shop(models.Model):
    class Meta:
        verbose_name = "Shop"
        verbose_name_plural = "Shops"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, auto_created=True)
    name = models.CharField(max_length=100)
    affiliation = models.CharField(
        max_length=20,
        choices=Affiliation.choices,
        default=Affiliation.TRADEDOUBLER
    )
    tracking_url = models.TextField(max_length=1000, default=None, blank=True)
    show_on_smartphones = models.BooleanField(default=True)
    scrape = models.BooleanField(default=True)

    @property
    def affiliation_obj(self):
        if self.affiliation == Affiliation.TRADEDOUBLER.value:
            return Tradedoubler()
        if self.affiliation == Affiliation.CONVERTISER.value:
            return Convertiser()
        raise ValueError(f'Affiliation object: {self.affiliation.name} unavailable')

    def __str__(self):
        return f"{self.name}"


class Product(models.Model):
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        constraints = [
            models.UniqueConstraint(fields=["name"], name="unique_name"),
            models.UniqueConstraint(fields=["epi"], name="unique_epi"),
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, auto_created=True)
    name = models.CharField(max_length=100)
    base_names = ArrayField(
        base_field=models.CharField(max_length=100, default=str(name)),
        default=list,
        blank=True
    )
    search_names = ArrayField(
        base_field=models.CharField(max_length=100, default=str(name)),
        default=list,
        blank=True
    )
    search_words_any_to_exclude = ArrayField(
        models.CharField(max_length=1000, blank=True),
        default=list,
        blank=True
    )
    search_words_any_to_include = ArrayField(
        models.CharField(max_length=1000, blank=True),
        default=list,
        blank=True
    )
    search_words_all_to_include = ArrayField(
        models.CharField(max_length=1000, blank=True),
        default=list,
        blank=True
    )
    epi = models.CharField(max_length=32, default=generate_random_string, auto_created=True)
    price_lower_limit = models.FloatField(null=True, blank=True)  # applied to avoid scam offers
    scrape = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"


class OfferState(models.TextChoices):
    NOT_CHECKED = 'not checked', gettext_lazy('Not Checked')
    OUTDATED = 'outdated', gettext_lazy('Outdated')
    VALID = 'valid', gettext_lazy('Valid')


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
    state = models.CharField(choices=OfferState.choices, max_length=16, default=OfferState.NOT_CHECKED)
    state_check_time = models.DateTimeField("State check time", blank=True, default=timezone.now)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    @property
    def affiliation_url(self):
        return self.shop.affiliation_obj.get_url(
            base_url=self.shop.tracking_url,
            epi=self.product.epi,
            deep_link=self.url
        )
