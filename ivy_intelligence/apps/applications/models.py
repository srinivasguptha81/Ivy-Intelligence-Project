from django.db import models
from django.contrib.auth.models import User
from apps.opportunities.models import Opportunity


APPLICATION_STATUS = [
    ('PENDING', 'Pending Review'),
    ('SUBMITTED', 'Submitted'),
    ('IN_REVIEW', 'Under Review'),
    ('SHORTLISTED', 'Shortlisted'),
    ('SELECTED', 'Selected'),
    ('REJECTED', 'Rejected'),
    ('WITHDRAWN', 'Withdrawn'),
]


class Application(models.Model):
    """
    Tracks a student's application to an opportunity.
    Supports both manual and auto-submission.
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='PENDING')
    cover_letter = models.TextField(blank=True, help_text="Optional cover letter for this application")
    resume_used = models.FileField(upload_to='application_resumes/', blank=True, null=True)
    auto_submitted = models.BooleanField(default=False, help_text="Was this submitted via auto-fill?")
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, help_text="Internal notes about this application")

    class Meta:
        unique_together = ('student', 'opportunity')  # prevent duplicate applications
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.student.username} → {self.opportunity.title[:50]}"


class AutoFillLog(models.Model):
    """
    Log of auto-application attempts via form detection + Selenium.
    """
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    form_url = models.URLField()
    fields_detected = models.JSONField(default=list, help_text="List of form fields found")
    fields_filled = models.JSONField(default=list, help_text="List of fields we successfully filled")
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    attempted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"AutoFill [{status}] — {self.application}"
