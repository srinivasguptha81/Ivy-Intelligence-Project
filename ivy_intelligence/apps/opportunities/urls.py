from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('opportunities/', views.opportunity_list, name='opportunity_list'),
    path('opportunities/<int:pk>/', views.opportunity_detail, name='opportunity_detail'),
    path('opportunities/scrape/', views.trigger_scrape, name='trigger_scrape'),
    path('api/opportunities/', views.api_opportunities, name='api_opportunities'),
]
