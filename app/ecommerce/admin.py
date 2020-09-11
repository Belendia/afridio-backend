from django.contrib import admin
from ecommerce import models

admin.site.register(models.Order)
admin.site.register(models.OrderMedia)

