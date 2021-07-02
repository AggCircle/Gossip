from django.urls import path
from . import views

urlpatterns = [
    path('get_eight_characters', views.get_eight_characters, name="get_eight_characters"),
    path('create_wx_user', views.create_wx_user, name="create_wx_user"),
]