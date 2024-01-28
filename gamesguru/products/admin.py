from django.contrib import admin

from . import models


class ShopAdmin(admin.ModelAdmin):
    search_fields = ['id', 'name']
    readonly_fields = ('id', )
    list_display = ['name', 'affiliation', 'tracking_url', 'show_on_smartphones']


class ProductAdmin(admin.ModelAdmin):
    search_fields = ['id', 'name', 'base_name', 'search_name']
    readonly_fields = ('id',)
    list_display = ['name', 'epi', 'price_lower_limit', 'base_name', 'search_name', 'search_words_any_to_exclude', 'search_words_any_to_include', 'search_words_all_to_include']
    ordering = ('-name', )


class OfferAdmin(admin.ModelAdmin):
    search_fields = ['id', 'name', 'price', 'currency', 'pub_time', 'product__name', 'shop__name']
    readonly_fields = ('id',)
    list_display = ['name', 'price', 'currency', 'pub_time', 'state', 'state_check_time', 'url', 'affiliation_url', 'product', 'shop']
    ordering = ('-pub_time', '-price')


admin.site.register(models.Shop, ShopAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Offer, OfferAdmin)
