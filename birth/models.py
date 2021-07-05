from django.db import models
from django.contrib import admin


SEX_CHOICE = ((u'0', "未知"), (u'1', "男"), (u'2', "女"))


# Create your models here.
class UserWx(models.Model):
    id = models.AutoField(primary_key=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    nick_name = models.CharField(verbose_name="昵称", max_length=100, null=True)
    gender = models.CharField(verbose_name="性别", max_length=1, null=True, choices=SEX_CHOICE)
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
    list_display = ('id', 'nick_name', 'create_time', 'gender', 'avatar_url', 'city')


class UserDetailInfo(models.Model):
    id = models.AutoField(primary_key=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    birth_datetime = models.CharField(verbose_name="查询过的日期", max_length=400, null=True)
    user_wx = models.ForeignKey(UserWx, related_name='user_wx_detail', on_delete=models.PROTECT, verbose_name=u'用户名')

    class Meta:
        db_table = "user_detail_info"
        verbose_name = "用户的详细信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.birth_datetime


class UserDetailInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'create_time', 'birth_datetime', 'user_wx')
