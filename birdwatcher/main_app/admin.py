from django.contrib import admin

# Register your models here.
from .models import Bird, Feeding, Location, Photo

admin.site.register(Bird)
admin.site.register(Feeding)
admin.site.register(Location)
admin.site.register(Photo)