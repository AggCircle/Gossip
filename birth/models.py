from django.db import models
from django.contrib import admin


# Create your models here.
class UserWx(models.Model):
    id = models.AutoField(primary_key=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    nick_name = models.CharField(verbose_name="昵称", max_length=100, null=True)
    gender = models.CharField(verbose_name="性别", max_length=1, null=True)
    avatar_url = models.CharField(verbose_name="头像", max_length=300, null=True)
    city = models.CharField(verbose_name="城市", max_length=30, null=True)
    province = models.CharField(verbose_name="省份", max_length=30, null=True)
    country = models.CharField(verbose_name="国家", max_length=30, null=True)
    is_true_data = models.BooleanField(verbose_name="是否真是数据", default=True)

    class Meta:
        db_table = "user_wx"
        verbose_name = "小程序用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.nick_name


class UserWxAdmin(admin.ModelAdmin):
    def set_gender(self):
        if self.gender == '1':
            return '男'
        elif self.gender == '2':
            return '女'
        else:
            return '未知'

    set_gender.short_description = '性别'
    list_display = ('id', 'nick_name', 'create_time', 'set_gender', 'avatar_url', 'city')
