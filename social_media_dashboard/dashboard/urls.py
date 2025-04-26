from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    # path('login/', views.login_view, name='login'),
    # path('register/', views.register_view, name='register'),
    path('like/', views.like_post, name='like_post'),
]