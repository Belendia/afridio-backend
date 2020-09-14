from django.contrib import admin
from ecommerce import models


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'refund_requested',
                    'refund_granted',
                    'billing_address',
                    'payment',
                    'coupon'
                    ]
    list_display_links = [
        'user',
        'billing_address',
        'payment',
        'coupon'
    ]
    list_filter = ['ordered',
                   'refund_requested',
                   'refund_granted']
    search_fields = [
        'user__email',
        'ref_code'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip',
        'default'
    ]
    list_filter = ['default', 'country']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']


admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.OrderMedia)
admin.site.register(models.Address, AddressAdmin)
admin.site.register(models.Payment)
admin.site.register(models.Coupon)
admin.site.register(models.Refund)
admin.site.register(models.UserProfile)
