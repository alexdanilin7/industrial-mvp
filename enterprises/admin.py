from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Enterprise, FinancialKPI, PropertyInfo, ProductInfo, GeoLocation

admin.site.register(Enterprise)
admin.site.register(FinancialKPI)
admin.site.register(PropertyInfo)
admin.site.register(ProductInfo)
admin.site.register(GeoLocation)