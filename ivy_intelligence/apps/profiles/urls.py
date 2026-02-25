from django.urls import path
from . import views

urlpatterns = [
    path('setup/', views.profile_setup, name='profile_setup'),
    path('edit/', views.profile_edit, name='profile_edit'),
    path('me/', views.my_profile, name='my_profile'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('<str:username>/', views.profile_view, name='profile_view'),
]
