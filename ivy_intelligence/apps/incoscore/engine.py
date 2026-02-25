"""
InCoScore (Intelligent Competency Score) Calculation Engine.

Formula:
    InCoScore = Σ [(achievement_raw_score / category_max) × category_weight × 100]
    Normalized to 0-100 scale.

Category Weights:
    Research Papers:  30%
    Hackathon Wins:   25%
    Internships:      20%
    Competitive Coding: 15%
    Conferences:      10%
    Certifications:   5%
    Projects:         5%
    Awards:           10%
    (Note: exceeds 100% because CGPA bonus is additive)

CGPA Bonus: Up to 5 additional points for CGPA >= 9.0
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

CATEGORY_WEIGHTS = {
    'RESEARCH': 0.30,
    'HACKATHON': 0.25,
    'INTERNSHIP': 0.20,
    'CODING': 0.15,
    'CONFERENCE': 0.10,
    'CERTIFICATION': 0.05,
    'PROJECT': 0.05,
    'AWARD': 0.10,
}


def calculate_incoscore(student_profile) -> float:
    """
    Calculate the InCoScore for a given StudentProfile.

    Steps:
    1. Fetch all verified achievements for the student
    2. For each achievement, compute contribution = (raw_score / 100) * weight * 100
    3. Sum all contributions, cap at 95 (5 points reserved for CGPA bonus)
    4. Add CGPA bonus (up to 5 points)
    5. Round to 2 decimal places

    Returns: float between 0.0 and 100.0
    """
    from apps.incoscore.models import Achievement

    achievements = Achievement.objects.filter(
        student=student_profile,
        verified=True,
        raw_score__gt=0,
    )

    if not achievements.exists():
        return 0.0

    # Group achievements by category, take the best score per category
    # (Prevents gaming by adding many low-value achievements)
    category_scores = {}
    for achievement in achievements:
        cat = achievement.category
        if cat not in category_scores or achievement.raw_score > category_scores[cat]:
            category_scores[cat] = achievement.raw_score

    # Calculate weighted score
    total_score = 0.0
    for category, raw_score in category_scores.items():
        weight = CATEGORY_WEIGHTS.get(category, 0)
        contribution = (raw_score / 100.0) * weight * 100
        total_score += contribution

    # Cap base score at 95
    total_score = min(total_score, 95.0)

    # CGPA Bonus: up to 5 points for CGPA >= 9.0
    cgpa = student_profile.cgpa or 0
    if cgpa >= 9.0:
        total_score += 5.0
    elif cgpa >= 8.0:
        total_score += 3.0
    elif cgpa >= 7.0:
        total_score += 1.0

    final_score = round(min(total_score, 100.0), 2)
    return final_score


def update_student_score(student_profile, reason: str = "Recalculation") -> float:
    """
    Recalculate and save a student's InCoScore.
    Also records the history for trend analysis.
    """
    from apps.incoscore.models import ScoreHistory

    old_score = student_profile.incoscore
    new_score = calculate_incoscore(student_profile)

    student_profile.incoscore = new_score
    student_profile.save(update_fields=['incoscore'])

    # Only record history if score changed
    if old_score != new_score:
        ScoreHistory.objects.create(
            student=student_profile,
            score=new_score,
            reason=f"{reason} (was {old_score})"
        )
        logger.info(f"Updated InCoScore for {student_profile.user.username}: {old_score} → {new_score}")

    return new_score


def get_score_breakdown(student_profile) -> dict:
    """
    Returns a detailed breakdown of InCoScore components.
    Used to display in the student's profile/dashboard.
    """
    from apps.incoscore.models import Achievement

    achievements = Achievement.objects.filter(student=student_profile, verified=True)
    breakdown = {}

    category_scores = {}
    for achievement in achievements:
        cat = achievement.category
        if cat not in category_scores or achievement.raw_score > category_scores[cat]:
            category_scores[cat] = achievement.raw_score

    for cat, weight in CATEGORY_WEIGHTS.items():
        raw = category_scores.get(cat, 0)
        contribution = round((raw / 100.0) * weight * 100, 2)
        breakdown[cat] = {
            'raw_score': raw,
            'weight': f"{int(weight * 100)}%",
            'contribution': contribution,
            'max_contribution': round(weight * 100, 2),
        }

    # CGPA bonus
    cgpa = student_profile.cgpa or 0
    cgpa_bonus = 5.0 if cgpa >= 9.0 else (3.0 if cgpa >= 8.0 else (1.0 if cgpa >= 7.0 else 0))
    breakdown['CGPA_BONUS'] = {
        'raw_score': cgpa,
        'weight': 'Bonus',
        'contribution': cgpa_bonus,
        'max_contribution': 5.0,
    }

    return breakdown


def get_leaderboard(limit: int = 50) -> list:
    """Return top students sorted by InCoScore."""
    from apps.profiles.models import StudentProfile
    return StudentProfile.objects.filter(
        incoscore__gt=0
    ).select_related('user').order_by('-incoscore')[:limit]


def get_recommendations(student_profile, limit: int = 5) -> list:
    """
    Recommend opportunities to a student based on their domain and InCoScore level.
    Higher InCoScore students get recommended more competitive opportunities.
    """
    from apps.opportunities.models import Opportunity

    domains = student_profile.domains_of_interest or []
    score = student_profile.incoscore

    qs = Opportunity.objects.filter(is_active=True)
    if domains:
        qs = qs.filter(domain__in=domains)

    # Higher scoring students see more prestigious opportunities
    if score >= 70:
        qs = qs.filter(opportunity_type__in=['FELLOWSHIP', 'SCHOLARSHIP', 'INTERNSHIP'])
    elif score >= 40:
        qs = qs.filter(opportunity_type__in=['WORKSHOP', 'HACKATHON', 'INTERNSHIP'])
    else:
        qs = qs.filter(opportunity_type__in=['WORKSHOP', 'HACKATHON', 'CONFERENCE'])

    return list(qs[:limit])
