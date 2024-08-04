from django.contrib import admin
from .models import AirQualityData, APIResponse , Favorite

# Register your models here.

admin.site.register(AirQualityData)
admin.site.register(APIResponse)
admin.site.register(Favorite)
