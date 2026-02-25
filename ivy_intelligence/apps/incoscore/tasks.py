from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def recalculate_all_scores():
    """
    Celery task: Recalculate InCoScore for ALL students.
    Runs daily at 2 AM via Celery Beat.
    """
    from apps.profiles.models import StudentProfile
    from apps.incoscore.engine import update_student_score

    profiles = StudentProfile.objects.all()
    updated = 0
    for profile in profiles:
        try:
            update_student_score(profile, reason="Nightly recalculation")
            updated += 1
        except Exception as e:
            logger.error(f"Score update failed for {profile.user.username}: {e}")

    logger.info(f"Recalculated scores for {updated} students")
    return {'updated': updated}


@shared_task
def verify_achievement(achievement_id: int):
    """
    Auto-verify an achievement by checking the proof URL.
    (Simplified — in production, this would do real verification.)
    """
    from apps.incoscore.models import Achievement
    from apps.incoscore.engine import update_student_score
    try:
        achievement = Achievement.objects.get(pk=achievement_id)
        if achievement.proof_url:
            import requests
            resp = requests.head(achievement.proof_url, timeout=5)
            if resp.status_code == 200:
                achievement.verified = True
                achievement.verified_by = "AutoVerify"
                achievement.save()
                update_student_score(achievement.student, reason=f"Achievement verified: {achievement.title}")
    except Exception as e:
        logger.error(f"Auto-verify failed for achievement {achievement_id}: {e}")
