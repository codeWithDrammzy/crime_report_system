from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


# ===================== Custom User Model =======================
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Super Admin'),
        ('officer', 'Officer'),
        ('citizen', 'Citizen'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='citizen')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"


# ===================== Police Department =======================
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=150)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    established_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Suspended'})"


# ===================== Police Officer =======================
class Officer(models.Model):
    RANK_CHOICES = [
        ('ASP', 'Assistant Superintendent of Police'),
        ('DSP', 'Deputy Superintendent of Police'),
        ('SP', 'Superintendent of Police'),
        ('CSP', 'Chief Superintendent of Police'),
        ('ACP', 'Assistant Commissioner of Police'),
        ('DCP', 'Deputy Commissioner of Police'),
        ('CP', 'Commissioner of Police'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rank = models.CharField(max_length=50, choices=RANK_CHOICES)
    badge_number = models.CharField(max_length=30, unique=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='officers')
    profile_picture = models.ImageField(upload_to='officers/', blank=True, null=True)
    on_duty = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.rank}"


# ===================== Crime Report =======================
class CrimeReport(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Investigating', 'Investigating'),
        ('Resolved', 'Resolved'),
    )

    INCIDENT_TYPES = [
        ('CR-TEMP', 'CR-TEMP'),
        ('ASSAULT', 'Assault'),
        ('BURGLARY', 'Burglary'),
        ('THEFT', 'Theft'),
    ]

    report_id = models.CharField(max_length=12, unique=True, editable=False)
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=255)
    incident_type = models.CharField(max_length=50, choices=INCIDENT_TYPES)  # ✅ FIXED HERE
    evidence_image = models.ImageField(upload_to='evidence/images/', null=True, blank=True)
    evidence_video = models.FileField(upload_to='evidence/videos/', null=True, blank=True)
    evidence_audio = models.FileField(upload_to='evidence/audio/', null=True, blank=True)
    
    date_reported = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def save(self, *args, **kwargs):
        if not self.report_id:
            self.report_id = f"CR-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.report_id})"

    class Meta:
        ordering = ['-date_reported']
