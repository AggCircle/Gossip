from django.contrib import admin
from birth.models import UserWx, UserWxAdmin, UserDetailInfo, UserDetailInfoAdmin


admin.site.register(UserWx, UserWxAdmin)
admin.site.register(UserDetailInfo, UserDetailInfoAdmin)

# Register your models here.
