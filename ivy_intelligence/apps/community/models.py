from django.db import models
from django.contrib.auth.models import User


DOMAIN_CHOICES = [
    ('AI', 'Artificial Intelligence'),
    ('LAW', 'Law'),
    ('BIO', 'Biomedical'),
    ('ECE', 'Electronics & Communication'),
    ('CS', 'Computer Science'),
    ('BUSINESS', 'Business & Management'),
    ('ENV', 'Environmental Science'),
    ('GENERAL', 'General'),
]


class DomainGroup(models.Model):
    """Domain-specific academic group (e.g., AI Research Group, Law Society)."""
    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES)
    description = models.TextField()
    members = models.ManyToManyField(User, blank=True, related_name='joined_groups')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def member_count(self):
        return self.members.count()


class Post(models.Model):
    """Academic community post — achievements, questions, updates."""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=2000)
    domain_tag = models.CharField(max_length=20, choices=DOMAIN_CHOICES, default='GENERAL')
    group = models.ForeignKey(DomainGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    likes = models.ManyToManyField(User, blank=True, related_name='liked_posts')
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username}: {self.content[:60]}"

    def like_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.count()


class Comment(models.Model):
    """Comment on a community post."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"


class ChatMessage(models.Model):
    """
    Real-time chat message within a domain group.
    Persisted in DB for history — also sent via WebSocket.
    """
    group = models.ForeignKey(DomainGroup, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(max_length=1000)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sent_at']

    def __str__(self):
        return f"[{self.group.name}] {self.sender.username}: {self.message[:40]}"
