from django.contrib import admin

from . import models


class ShopAdmin(admin.ModelAdmin):
    search_fields = ['id', 'name']
    readonly_fields = ('id', )
    list_display = ['name', 'tracking_url']


class ProductAdmin(admin.ModelAdmin):
    search_fields = ['id', 'name']
    readonly_fields = ('id',)
    list_display = ['name', 'epi']
    ordering = ('-name', )


class OfferAdmin(admin.ModelAdmin):
    search_fields = ['id', 'name']
    readonly_fields = ('id',)
    list_display = ['name', 'price', 'currency', 'url', 'affiliation_url', 'pub_time']
    ordering = ('-pub_time', )


admin.site.register(models.Shop, ShopAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Offer, OfferAdmin)
