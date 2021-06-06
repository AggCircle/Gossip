from django.urls import path
from . import views


urlpatterns = [
	path('get_eight_characters', views.get_eight_characters, name="get_eight_characters"),
]