from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


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

YEAR_CHOICES = [
    ('1', '1st Year'),
    ('2', '2nd Year'),
    ('3', '3rd Year'),
    ('4', '4th Year'),
    ('PG', 'Postgraduate'),
    ('PHD', 'PhD'),
]


class StudentProfile(models.Model):
    """Extended profile for each user. Created automatically on user registration."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, max_length=500)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    university = models.CharField(max_length=200, blank=True)
    year_of_study = models.CharField(max_length=5, choices=YEAR_CHOICES, blank=True)
    cgpa = models.FloatField(null=True, blank=True, help_text="On a 10 point scale")
    domains_of_interest = models.JSONField(default=list, help_text="List of domain codes")
    skills = models.JSONField(default=list, help_text="List of skill strings")
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    incoscore = models.FloatField(default=0.0)
    profile_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_domain_names(self):
        """Return human-readable domain names."""
        domain_map = dict(DOMAIN_CHOICES)
        return [domain_map.get(d, d) for d in self.domains_of_interest]

    def calculate_profile_completeness(self):
        """Check if the profile is complete enough for applications."""
        required = [self.bio, self.university, self.domains_of_interest, self.skills]
        return all(required)

    def save(self, *args, **kwargs):
        self.profile_complete = self.calculate_profile_completeness()
        super().save(*args, **kwargs)


@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    """Automatically create a StudentProfile when a new User registers."""
    if created:
        StudentProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_student_profile(sender, instance, **kwargs):
    """Automatically save profile when user is saved."""
    if hasattr(instance, 'studentprofile'):
        instance.studentprofile.save()
