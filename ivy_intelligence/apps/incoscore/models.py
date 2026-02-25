from django.db import models
from apps.profiles.models import StudentProfile


ACHIEVEMENT_CATEGORIES = [
    ('RESEARCH', 'Research Paper Published'),
    ('HACKATHON', 'Hackathon / Competition Win'),
    ('INTERNSHIP', 'Internship Completed'),
    ('CODING', 'Competitive Coding'),
    ('CONFERENCE', 'Conference Participation'),
    ('CERTIFICATION', 'Certification / Course'),
    ('PROJECT', 'Open Source / Project'),
    ('AWARD', 'Award / Recognition'),
]

# Weight of each category in InCoScore calculation
# Must sum to 1.0
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

# Maximum raw points per category (for normalization)
CATEGORY_MAX_POINTS = {
    'RESEARCH': 100,
    'HACKATHON': 100,
    'INTERNSHIP': 100,
    'CODING': 100,
    'CONFERENCE': 100,
    'CERTIFICATION': 100,
    'PROJECT': 100,
    'AWARD': 100,
}


class Achievement(models.Model):
    """
    A verified academic achievement that contributes to a student's InCoScore.
    Admin or automated system must verify each achievement.
    """
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='achievements')
    category = models.CharField(max_length=20, choices=ACHIEVEMENT_CATEGORIES)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    proof_url = models.URLField(blank=True, help_text="Link to certificate, paper, or result")
    proof_file = models.FileField(upload_to='achievement_proofs/', blank=True, null=True)
    raw_score = models.FloatField(default=10.0, help_text="Raw score 0-100 for this achievement")
    verified = models.BooleanField(default=False)
    verified_by = models.CharField(max_length=100, blank=True)
    achieved_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.user.username} — {self.get_category_display()}: {self.title[:50]}"

    def contribution_to_incoscore(self):
        """How many InCoScore points does this achievement contribute?"""
        weight = CATEGORY_WEIGHTS.get(self.category, 0)
        max_pts = CATEGORY_MAX_POINTS.get(self.category, 100)
        return round((self.raw_score / max_pts) * weight * 100, 2)


class ScoreHistory(models.Model):
    """Track InCoScore changes over time for analytics."""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='score_history')
    score = models.FloatField()
    recorded_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.student.user.username}: {self.score} at {self.recorded_at.date()}"
