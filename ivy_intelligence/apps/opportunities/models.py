from django.db import models


DOMAIN_CHOICES = [
    ('AI', 'Artificial Intelligence'),
    ('LAW', 'Law'),
    ('BIO', 'Biomedical'),
    ('ECE', 'Electronics & Communication'),
    ('CS', 'Computer Science'),
    ('BUSINESS', 'Business & Management'),
    ('ENV', 'Environmental Science'),
    ('OTHER', 'Other'),
]

OPPORTUNITY_TYPES = [
    ('INTERNSHIP', 'Research Internship'),
    ('HACKATHON', 'Hackathon'),
    ('WORKSHOP', 'Workshop'),
    ('CONFERENCE', 'Conference'),
    ('SCHOLARSHIP', 'Scholarship'),
    ('FELLOWSHIP', 'Fellowship'),
    ('COMPETITION', 'Competition'),
    ('OTHER', 'Other'),
]

IVY_UNIVERSITIES = [
    ('HARVARD', 'Harvard University'),
    ('MIT', 'MIT'),
    ('YALE', 'Yale University'),
    ('PRINCETON', 'Princeton University'),
    ('COLUMBIA', 'Columbia University'),
    ('CORNELL', 'Cornell University'),
    ('STANFORD', 'Stanford University'),
    ('PENN', 'University of Pennsylvania'),
    ('DARTMOUTH', 'Dartmouth College'),
    ('BROWN', 'Brown University'),
]


class Opportunity(models.Model):
    title = models.CharField(max_length=300)
    university = models.CharField(max_length=50, choices=IVY_UNIVERSITIES)
    domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES, default='OTHER')
    opportunity_type = models.CharField(max_length=20, choices=OPPORTUNITY_TYPES, default='OTHER')
    description = models.TextField()
    deadline = models.DateField(null=True, blank=True)
    source_url = models.URLField(unique=True)
    is_active = models.BooleanField(default=True)
    scraped_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    stipend = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True, default='Remote / On-campus')

    class Meta:
        ordering = ['-scraped_at']
        verbose_name_plural = 'Opportunities'

    def __str__(self):
        return f"{self.title} — {self.get_university_display()}"

    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]


class ScrapingLog(models.Model):
    """Track each scraping run for debugging and monitoring."""
    university = models.CharField(max_length=50)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    opportunities_found = models.IntegerField(default=0)
    new_opportunities = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='RUNNING',
                              choices=[('RUNNING','Running'),('SUCCESS','Success'),('FAILED','Failed')])
    error_message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.university} scrape — {self.started_at.strftime('%Y-%m-%d %H:%M')}"
