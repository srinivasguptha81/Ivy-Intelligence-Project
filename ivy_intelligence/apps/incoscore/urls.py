from django.urls import path
from . import views

urlpatterns = [
    path('', views.incoscore_dashboard, name='incoscore_dashboard'),
    path('add/', views.add_achievement, name='add_achievement'),
    path('delete/<int:achievement_id>/', views.delete_achievement, name='delete_achievement'),
    path('leaderboard/', views.global_leaderboard, name='global_leaderboard'),
    path('api/my-score/', views.api_my_score, name='api_my_score'),
]
