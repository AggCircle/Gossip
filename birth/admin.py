from django.contrib import admin
from birth.models import UserWx, UserWxAdmin


admin.site.register(UserWx, UserWxAdmin)

# Register your models here.
