from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import Achievement, ScoreHistory, ACHIEVEMENT_CATEGORIES
from .engine import update_student_score, get_score_breakdown, get_leaderboard, get_recommendations


def _get_profile(user):
    from apps.profiles.models import StudentProfile
    profile, _ = StudentProfile.objects.get_or_create(user=user)
    return profile


@login_required
def incoscore_dashboard(request):
    profile  = _get_profile(request.user)
    achievements = Achievement.objects.filter(student=profile)
    history  = ScoreHistory.objects.filter(student=profile).order_by('-recorded_at')[:10]

    try:
        breakdown     = get_score_breakdown(profile)
        recommendations = get_recommendations(profile)
        update_student_score(profile, reason="Dashboard visit")
    except Exception:
        breakdown = {}
        recommendations = []

    return render(request, 'incoscore/dashboard.html', {
        'profile':          profile,
        'achievements':     achievements,
        'verified_count':   achievements.filter(verified=True).count(),
        'pending_count':    achievements.filter(verified=False).count(),
        'history':          history,
        'breakdown':        breakdown,
        'recommendations':  recommendations,
        'categories':       ACHIEVEMENT_CATEGORIES,
    })


@login_required
def add_achievement(request):
    if request.method == 'POST':
        profile  = _get_profile(request.user)
        title    = request.POST.get('title', '').strip()
        category = request.POST.get('category', '')
        if not title or not category:
            messages.error(request, "Title and category are required.")
            return redirect('incoscore_dashboard')
        Achievement.objects.create(
            student     = profile,
            title       = title,
            category    = category,
            description = request.POST.get('description', ''),
            proof_url   = request.POST.get('proof_url', ''),
            proof_file  = request.FILES.get('proof_file'),
            achieved_on = request.POST.get('achieved_on') or None,
            verified    = False,
        )
        messages.success(request, "Achievement submitted! Awaiting admin verification.")
    return redirect('incoscore_dashboard')


@login_required
def delete_achievement(request, achievement_id):
    profile     = _get_profile(request.user)
    achievement = get_object_or_404(Achievement, pk=achievement_id, student=profile)
    if achievement.verified:
        messages.error(request, "Cannot delete a verified achievement.")
    else:
        achievement.delete()
        messages.success(request, "Achievement removed.")
    return redirect('incoscore_dashboard')


def global_leaderboard(request):
    return render(request, 'incoscore/leaderboard.html', {
        'top_students': get_leaderboard(limit=100),
    })


@login_required
def api_my_score(request):
    profile   = _get_profile(request.user)
    breakdown = get_score_breakdown(profile)
    return JsonResponse({
        'username':   request.user.username,
        'incoscore':  profile.incoscore,
        'breakdown':  breakdown,
    })
