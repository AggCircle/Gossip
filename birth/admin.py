from django.contrib import admin
import birth.models as models


admin.site.register(models.UserWx, models.UserWxAdmin)
admin.site.register(models.UserDetailInfo, models.UserDetailInfoAdmin)
admin.site.register(models.UserComments, models.UserCommentsAdmin)
admin.site.register(models.LeaveMessage, models.LeaveMessageAdmin)

# Register your models here.
