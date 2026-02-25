"""
Real-Time Web Scraper for Ivy League University Opportunities.

Each scraper function targets a specific university's events/opportunities page.
We use requests + BeautifulSoup4 to fetch and parse HTML.
Change detection: we store source_url as unique, so duplicates are auto-skipped.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import logging
import time

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    )
}

TIMEOUT = 15  # seconds


def safe_get(url):
    """Fetch a URL safely, returning None on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None


def scrape_harvard():
    """
    Scrape Harvard University events and opportunities.
    Target: Harvard Office of Career Services & SEAS events page.
    Returns a list of opportunity dicts.
    """
    opportunities = []
    urls = [
        'https://www.harvard.edu/events/',
        'https://seas.harvard.edu/news-events/events',
    ]

    for url in urls:
        resp = safe_get(url)
        if not resp:
            continue
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Harvard events use article tags with specific classes
        events = soup.find_all('article', class_=lambda c: c and 'event' in c.lower())
        if not events:
            # fallback: look for list items or divs with event data
            events = soup.find_all(['div', 'li'], class_=lambda c: c and 'event' in str(c).lower())

        for event in events[:20]:  # limit to 20 per page
            title_tag = event.find(['h2', 'h3', 'h4', 'a'])
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            if len(title) < 5:
                continue

            link_tag = event.find('a', href=True)
            if not link_tag:
                continue
            href = link_tag['href']
            if not href.startswith('http'):
                href = 'https://www.harvard.edu' + href

            desc_tag = event.find(['p', 'div'], class_=lambda c: c and 'desc' in str(c).lower())
            description = desc_tag.get_text(strip=True) if desc_tag else title

            opportunities.append({
                'title': title,
                'university': 'HARVARD',
                'description': description or title,
                'source_url': href,
                'location': 'Cambridge, MA / Remote',
                'opportunity_type': classify_type(title),
            })

    logger.info(f"Harvard scraper found {len(opportunities)} opportunities")
    return opportunities


def scrape_mit():
    """
    Scrape MIT Events and opportunities.
    Target: MIT events.mit.edu
    """
    opportunities = []
    url = 'https://events.mit.edu/'
    resp = safe_get(url)
    if not resp:
        return opportunities

    soup = BeautifulSoup(resp.text, 'html.parser')

    # MIT events page uses specific structure
    event_links = soup.find_all('a', href=True)
    seen = set()

    for link in event_links:
        href = link['href']
        if '/event/' not in href and '/events/' not in href:
            continue
        if href in seen:
            continue
        seen.add(href)

        title = link.get_text(strip=True)
        if len(title) < 5 or len(title) > 300:
            continue

        full_url = href if href.startswith('http') else f'https://events.mit.edu{href}'
        opportunities.append({
            'title': title,
            'university': 'MIT',
            'description': f"MIT event: {title}",
            'source_url': full_url,
            'location': 'Cambridge, MA / Remote',
            'opportunity_type': classify_type(title),
        })

    logger.info(f"MIT scraper found {len(opportunities)} opportunities")
    return opportunities[:30]


def scrape_stanford():
    """
    Scrape Stanford University events.
    Target: Stanford Events calendar.
    """
    opportunities = []
    url = 'https://events.stanford.edu/'
    resp = safe_get(url)
    if not resp:
        return opportunities

    soup = BeautifulSoup(resp.text, 'html.parser')
    events = soup.find_all(['article', 'div', 'li'], class_=lambda c: c and 'event' in str(c).lower())

    for event in events[:25]:
        title_tag = event.find(['h2', 'h3', 'h4', 'a'])
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        if len(title) < 5:
            continue

        link_tag = event.find('a', href=True)
        href = link_tag['href'] if link_tag else '#'
        if not href.startswith('http'):
            href = 'https://events.stanford.edu' + href

        desc_tag = event.find('p')
        description = desc_tag.get_text(strip=True) if desc_tag else title

        opportunities.append({
            'title': title,
            'university': 'STANFORD',
            'description': description,
            'source_url': href,
            'location': 'Stanford, CA / Remote',
            'opportunity_type': classify_type(title),
        })

    logger.info(f"Stanford scraper found {len(opportunities)} opportunities")
    return opportunities


def scrape_yale():
    """
    Scrape Yale University opportunities.
    Target: Yale career and events pages.
    """
    opportunities = []
    url = 'https://yale.edu/academics/resources'
    resp = safe_get(url)
    if not resp:
        return opportunities

    soup = BeautifulSoup(resp.text, 'html.parser')
    links = soup.find_all('a', href=True)

    for link in links[:50]:
        title = link.get_text(strip=True)
        href = link['href']
        if len(title) < 10:
            continue
        if not any(kw in title.lower() for kw in ['internship', 'research', 'fellowship', 'scholarship', 'workshop', 'conference', 'hackathon']):
            continue

        full_url = href if href.startswith('http') else f'https://yale.edu{href}'
        opportunities.append({
            'title': title,
            'university': 'YALE',
            'description': f"Yale University opportunity: {title}",
            'source_url': full_url,
            'location': 'New Haven, CT / Remote',
            'opportunity_type': classify_type(title),
        })

    logger.info(f"Yale scraper found {len(opportunities)} opportunities")
    return opportunities[:20]


def classify_type(title: str) -> str:
    """
    Simple keyword-based opportunity type classifier.
    The ML classifier handles domain, this handles the event type.
    """
    title_lower = title.lower()
    if any(kw in title_lower for kw in ['internship', 'intern']):
        return 'INTERNSHIP'
    if any(kw in title_lower for kw in ['hackathon', 'hack']):
        return 'HACKATHON'
    if any(kw in title_lower for kw in ['workshop', 'bootcamp', 'training']):
        return 'WORKSHOP'
    if any(kw in title_lower for kw in ['conference', 'symposium', 'summit']):
        return 'CONFERENCE'
    if any(kw in title_lower for kw in ['scholarship', 'grant', 'funding']):
        return 'SCHOLARSHIP'
    if any(kw in title_lower for kw in ['fellowship']):
        return 'FELLOWSHIP'
    if any(kw in title_lower for kw in ['competition', 'contest', 'challenge']):
        return 'COMPETITION'
    return 'OTHER'


# Registry of all scrapers
SCRAPERS = {
    'HARVARD': scrape_harvard,
    'MIT': scrape_mit,
    'STANFORD': scrape_stanford,
    'YALE': scrape_yale,
}


def run_scraper(university_key: str) -> dict:
    """
    Run one university scraper, classify domains, save to DB.
    Returns stats dict.
    """
    from apps.opportunities.models import Opportunity, ScrapingLog
    from apps.opportunities.classifier import classify_domain

    log = ScrapingLog.objects.create(university=university_key, status='RUNNING')
    stats = {'found': 0, 'new': 0, 'errors': 0}

    try:
        scraper_fn = SCRAPERS.get(university_key)
        if not scraper_fn:
            raise ValueError(f"No scraper for university: {university_key}")

        raw_opportunities = scraper_fn()
        stats['found'] = len(raw_opportunities)

        for opp_data in raw_opportunities:
            # Skip if URL already exists (change detection)
            if Opportunity.objects.filter(source_url=opp_data['source_url']).exists():
                continue

            # Classify domain using AI classifier
            domain = classify_domain(opp_data.get('description', '') + ' ' + opp_data.get('title', ''))

            Opportunity.objects.create(
                title=opp_data['title'][:300],
                university=opp_data['university'],
                domain=domain,
                opportunity_type=opp_data.get('opportunity_type', 'OTHER'),
                description=opp_data.get('description', ''),
                source_url=opp_data['source_url'],
                location=opp_data.get('location', 'Remote'),
                is_active=True,
            )
            stats['new'] += 1

        log.opportunities_found = stats['found']
        log.new_opportunities = stats['new']
        log.status = 'SUCCESS'

    except Exception as e:
        stats['errors'] += 1
        log.status = 'FAILED'
        log.error_message = str(e)
        logger.error(f"Scraper failed for {university_key}: {e}")

    finally:
        from django.utils import timezone
        log.finished_at = timezone.now()
        log.save()

    return stats
