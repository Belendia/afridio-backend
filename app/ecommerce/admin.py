from django.contrib import admin
from ecommerce import models

admin.site.register(models.Order)
admin.site.register(models.OrderMedia)
admin.site.register(models.Address)
admin.site.register(models.Payment)
admin.site.register(models.Coupon)
admin.site.register(models.Refund)
admin.site.register(models.UserProfile)
