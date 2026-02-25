from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

from .models import StudentProfile, DOMAIN_CHOICES

YEAR_CHOICES = [
    ('1', '1st Year'), ('2', '2nd Year'), ('3', '3rd Year'),
    ('4', '4th Year'), ('PG', 'Postgraduate'), ('PHD', 'PhD'),
]


def _get_profile(user):
    profile, _ = StudentProfile.objects.get_or_create(user=user)
    return profile


@login_required
def profile_setup(request):
    return profile_edit(request)


@login_required
def profile_edit(request):
    profile = _get_profile(request.user)

    if request.method == 'POST':
        # User fields
        request.user.first_name = request.POST.get('first_name', '').strip()
        request.user.last_name  = request.POST.get('last_name', '').strip()
        request.user.email      = request.POST.get('email', '').strip()
        request.user.save()

        # Profile text fields
        profile.bio            = request.POST.get('bio', '').strip()
        profile.university     = request.POST.get('university', '').strip()
        profile.year_of_study  = request.POST.get('year_of_study', '')
        profile.linkedin_url   = request.POST.get('linkedin_url', '').strip()
        profile.github_url     = request.POST.get('github_url', '').strip()

        # CGPA
        cgpa_raw = request.POST.get('cgpa', '').strip()
        try:
            profile.cgpa = float(cgpa_raw) if cgpa_raw else None
        except ValueError:
            profile.cgpa = None

        # Skills
        skills_str = request.POST.get('skills_input', '')
        profile.skills = [s.strip() for s in skills_str.split(',') if s.strip()]

        # Domains (multiple checkboxes)
        profile.domains_of_interest = request.POST.getlist('domains_of_interest')

        # File uploads
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        if 'resume' in request.FILES:
            profile.resume = request.FILES['resume']

        profile.save()
        messages.success(request, "Profile saved successfully! ✓")
        return redirect('profile_view', username=request.user.username)

    return render(request, 'profiles/edit.html', {
        'profile': profile,
        'domain_choices': DOMAIN_CHOICES,
        'year_choices': YEAR_CHOICES,
    })


def profile_view(request, username):
    user    = get_object_or_404(User, username=username)
    profile = _get_profile(user)

    from apps.incoscore.models import Achievement
    achievements = Achievement.objects.filter(student=profile, verified=True)

    from apps.community.models import Post
    posts = Post.objects.filter(author=user, is_active=True).order_by('-created_at')[:5]

    from apps.applications.models import Application
    applications_count = Application.objects.filter(student=user).count()

    return render(request, 'profiles/view.html', {
        'profile': profile,
        'profile_user': user,
        'achievements': achievements,
        'posts': posts,
        'applications_count': applications_count,
        'is_own_profile': request.user == user,
    })


@login_required
def my_profile(request):
    return redirect('profile_view', username=request.user.username)


def leaderboard(request):
    profiles = StudentProfile.objects.filter(
        incoscore__gt=0
    ).order_by('-incoscore').select_related('user')[:50]
    return render(request, 'profiles/leaderboard.html', {'profiles': profiles})
