from django.urls import path
from . import views

urlpatterns = [
    path('get_eight_characters', views.get_eight_characters, name="get_eight_characters"),
    path('create_wx_user', views.create_wx_user, name="create_wx_user"),
    path('on_login', views.on_login, name="on_login"),
    path('get_user_comments', views.get_user_comments, name="get_user_comments"),
    path('insert_user_comment', views.insert_user_comment, name="insert_user_comment"),
    path('create_leave_message', views.create_leave_message, name="create_leave_message"),
    path('avoid_star', views.avoid_star, name="avoid_star"),
]
