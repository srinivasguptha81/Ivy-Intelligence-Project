"""
Celery tasks for periodic scraping of Ivy League opportunities.

Run worker: celery -A config worker -l info
Run beat:   celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
"""

from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def scrape_university(self, university_key: str):
    """
    Scrape a single university's opportunities.
    Retries up to 3 times on failure (with 5-minute delay).
    """
    try:
        from apps.opportunities.scraper import run_scraper
        stats = run_scraper(university_key)
        logger.info(f"Scraped {university_key}: {stats}")
        return stats
    except Exception as exc:
        logger.error(f"Task failed for {university_key}: {exc}")
        raise self.retry(exc=exc)


@shared_task
def scrape_all_universities():
    """
    Master task: kicks off scraping for all supported universities.
    Called by Celery Beat every 6 hours.
    """
    from apps.opportunities.scraper import SCRAPERS
    results = {}
    for university_key in SCRAPERS.keys():
        result = scrape_university.delay(university_key)
        results[university_key] = result.id
    logger.info(f"Launched scraping tasks for: {list(SCRAPERS.keys())}")
    return results


@shared_task
def train_classifier_task():
    """
    Re-train the domain classifier.
    Can be triggered manually from admin or scheduled monthly.
    """
    from apps.opportunities.classifier import train_model
    success = train_model()
    return {'success': success}
