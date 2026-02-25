from django.contrib import admin
from .models import Post, Comment, DomainGroup, ChatMessage


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'domain_tag', 'like_count', 'comment_count', 'created_at', 'is_active')
    list_filter = ('domain_tag', 'is_active')
    search_fields = ('content', 'author__username')
    list_editable = ('is_active',)


@admin.register(DomainGroup)
class DomainGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain', 'member_count', 'created_at')
    list_filter = ('domain',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'group', 'sent_at')
    list_filter = ('group',)
