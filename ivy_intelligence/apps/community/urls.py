from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed, name='community_feed'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('groups/', views.groups_list, name='groups_list'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/join/', views.join_group, name='join_group'),
    path('groups/<int:group_id>/send/', views.send_message, name='send_message'),
    path('groups/<int:group_id>/messages/', views.get_messages, name='get_messages'),
]
