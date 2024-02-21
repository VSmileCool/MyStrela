from django.urls import path
from . import views

urlpatterns = [
    path('gallery/', views.gallery_view, name="user_gallery"),
    path('upload/', views.upload_view, name="upload"),
    path('', views.home_view, name="home"),
]
