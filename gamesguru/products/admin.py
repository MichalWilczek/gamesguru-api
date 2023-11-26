from django.contrib import admin

from . import models


class ShopAdmin(admin.ModelAdmin):
    search_fields = ['id', 'name']
    readonly_fields = ('id', )
    list_display = ['name', 'tracking_url']


class ProductCategoryAdmin(admin.ModelAdmin):
    search_fields = ['id', 'name']
    readonly_fields = ('id',)
    list_display = ['name']
    ordering = ('-name', )


class ProductAdmin(admin.ModelAdmin):
    search_fields = ['id', 'name', 'base_name', 'search_name']
    readonly_fields = ('id',)
    list_display = ['name', 'epi', 'category', 'price_lower_limit', 'base_name', 'search_name']
    ordering = ('-name', )


class OfferAdmin(admin.ModelAdmin):
    search_fields = ['id', 'name', 'price', 'currency', 'pub_time', 'product__name', 'shop__name']
    readonly_fields = ('id',)
    list_display = ['name', 'price', 'currency', 'url', 'affiliation_url', 'pub_time', 'product', 'shop']
    ordering = ('-pub_time', )


admin.site.register(models.Shop, ShopAdmin)
admin.site.register(models.ProductCategory, ProductCategoryAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Offer, OfferAdmin)
