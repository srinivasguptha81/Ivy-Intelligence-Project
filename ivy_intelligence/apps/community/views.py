from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import Post, Comment, DomainGroup, ChatMessage, DOMAIN_CHOICES


def _get_domains(user):
    try:
        from apps.profiles.models import StudentProfile
        profile, _ = StudentProfile.objects.get_or_create(user=user)
        return profile.domains_of_interest or []
    except Exception:
        return []


@login_required
def feed(request):
    user_domains = _get_domains(request.user)
    posts = Post.objects.filter(is_active=True).select_related('author')
    domain_filter = request.GET.get('domain', '')
    if domain_filter:
        posts = posts.filter(domain_tag=domain_filter)
    elif user_domains:
        posts = posts.filter(domain_tag__in=user_domains + ['GENERAL'])
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'community/feed.html', {
        'page_obj': page_obj,
        'domain_choices': DOMAIN_CHOICES,
        'domain_filter': domain_filter,
        'groups': DomainGroup.objects.all()[:10],
    })


@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        domain_tag = request.POST.get('domain_tag', 'GENERAL')
        group_id = request.POST.get('group_id')
        image = request.FILES.get('image')
        if not content:
            django_messages.error(request, "Post content cannot be empty.")
            return redirect('community_feed')
        post = Post.objects.create(author=request.user, content=content, domain_tag=domain_tag, image=image)
        if group_id:
            try:
                post.group = DomainGroup.objects.get(pk=group_id)
                post.save()
                return redirect('group_detail', group_id=group_id)
            except DomainGroup.DoesNotExist:
                pass
    return redirect('community_feed')


@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(Post, pk=post_id, is_active=True)
    if post.likes.filter(pk=request.user.pk).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': post.like_count()})


@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id, is_active=True)
    content = request.POST.get('content', '').strip()
    if content:
        comment = Comment.objects.create(post=post, author=request.user, content=content)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'username': request.user.username, 'content': comment.content})
    return redirect('community_feed')


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id, author=request.user)
    post.is_active = False
    post.save()
    return redirect('community_feed')


def groups_list(request):
    groups = DomainGroup.objects.all()
    domain_filter = request.GET.get('domain', '')
    if domain_filter:
        groups = groups.filter(domain=domain_filter)
    return render(request, 'community/groups.html', {
        'groups': groups,
        'domain_choices': DOMAIN_CHOICES,
        'domain_filter': domain_filter,
    })


@login_required
def group_detail(request, group_id):
    group = get_object_or_404(DomainGroup, pk=group_id)
    posts = Post.objects.filter(group=group, is_active=True)
    recent_messages = list(ChatMessage.objects.filter(group=group).order_by('-sent_at')[:30])
    recent_messages.reverse()
    is_member = group.members.filter(pk=request.user.pk).exists()
    return render(request, 'community/group_detail.html', {
        'group': group,
        'posts': posts,
        'recent_messages': recent_messages,
        'is_member': is_member,
        'domain_choices': DOMAIN_CHOICES,
    })


@login_required
def join_group(request, group_id):
    group = get_object_or_404(DomainGroup, pk=group_id)
    if group.members.filter(pk=request.user.pk).exists():
        group.members.remove(request.user)
        django_messages.info(request, f"Left {group.name}")
    else:
        group.members.add(request.user)
        django_messages.success(request, f"Joined {group.name}!")
    return redirect('group_detail', group_id=group_id)


@login_required
@require_POST
def send_message(request, group_id):
    """HTTP fallback for chat when WebSocket/Redis not available."""
    group = get_object_or_404(DomainGroup, pk=group_id)
    if not group.members.filter(pk=request.user.pk).exists():
        return JsonResponse({'ok': False, 'error': 'Not a member'}, status=403)
    msg_text = request.POST.get('message', '').strip()
    if not msg_text:
        return JsonResponse({'ok': False, 'error': 'Empty message'}, status=400)
    msg = ChatMessage.objects.create(group=group, sender=request.user, message=msg_text)
    return JsonResponse({
        'ok': True,
        'id': msg.pk,
        'username': request.user.username,
        'message': msg.message,
        'time': msg.sent_at.strftime('%H:%M'),
    })


@login_required
def get_messages(request, group_id):
    """Poll endpoint — returns messages newer than ?after=<id>."""
    group = get_object_or_404(DomainGroup, pk=group_id)
    after_id = int(request.GET.get('after', 0))
    msgs = ChatMessage.objects.filter(group=group, pk__gt=after_id).order_by('sent_at')[:50]
    return JsonResponse({
        'messages': [
            {'id': m.pk, 'username': m.sender.username, 'message': m.message, 'time': m.sent_at.strftime('%H:%M')}
            for m in msgs
        ]
    })
