from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
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
        ('Dismissed', 'Dismissed')
    )

    PRIORITY_CHOICES = (
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Emergency', 'Emergency')
    )

    INCIDENT_TYPES = [
        ('CR-TEMP', 'CR-TEMP'),
        ('ASSAULT', 'Assault'),
        ('BURGLARY', 'Burglary'),
        ('THEFT', 'Theft'),
        ('ROBBERY', 'Robbery'),
        ('VANDALISM', 'Vandalism'),
        ('FRAUD', 'Fraud'),
        ('CYBERCRIME', 'Cyber Crime'),
        ('DRUG_OFFENSE', 'Drug Offense'),
        ('TRAFFIC_ACCIDENT', 'Traffic Accident'),
        ('DOMESTIC_VIOLENCE', 'Domestic Violence'),
        ('HARASSMENT', 'Harassment'),
        ('OTHER', 'Other'),
    ]

    report_id = models.CharField(max_length=12, unique=True, editable=False)
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=255)
    
    # GPS Coordinates
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    incident_type = models.CharField(max_length=50, choices=INCIDENT_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    
    # Evidence Files
    evidence_image = models.ImageField(upload_to='evidence/images/%Y/%m/%d/', null=True, blank=True)
    evidence_video = models.FileField(upload_to='evidence/videos/%Y/%m/%d/', null=True, blank=True)
    evidence_audio = models.FileField(upload_to='evidence/audio/%Y/%m/%d/', null=True, blank=True)
    
    # Timestamps
    date_reported = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def save(self, *args, **kwargs):
        if not self.report_id:
            self.report_id = f"CR-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def get_google_maps_url(self):
        """Generate Google Maps URL from coordinates"""
        if self.latitude and self.longitude:
            return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
        return None

    def get_static_map_url(self, size="400x300", zoom=15):
        """Generate static map image URL (requires Google Maps API key in production)"""
        if self.latitude and self.longitude:
            # Note: You'll need to add your Google Maps API key in production
            api_key = "YOUR_GOOGLE_MAPS_API_KEY"  # Set this in settings.py
            return f"https://maps.googleapis.com/maps/api/staticmap?center={self.latitude},{self.longitude}&zoom={zoom}&size={size}&markers=color:red%7C{self.latitude},{self.longitude}&key={api_key}"
        return None

    def get_status_badge_class(self):
        """Return CSS class for status badge"""
        status_classes = {
            'Pending': 'bg-yellow-100 text-yellow-800',
            'Investigating': 'bg-blue-100 text-blue-800',
            'Resolved': 'bg-green-100 text-green-800',
            'Dismissed': 'bg-red-100 text-red-800',
        }
        return status_classes.get(self.status, 'bg-gray-100 text-gray-800')

    def get_priority_badge_class(self):
        """Return CSS class for priority badge"""
        priority_classes = {
            'Low': 'bg-green-100 text-green-800',
            'Medium': 'bg-yellow-100 text-yellow-800',
            'High': 'bg-orange-100 text-orange-800',
            'Emergency': 'bg-red-100 text-red-800',
        }
        return priority_classes.get(self.priority, 'bg-gray-100 text-gray-800')

    def get_evidence_count(self):
        """Count total evidence files attached"""
        count = 0
        if self.evidence_image:
            count += 1
        if self.evidence_video:
            count += 1
        if self.evidence_audio:
            count += 1
        return count

    def is_owned_by(self, user):
        """Check if user owns this report"""
        return self.reporter == user

    def can_be_accessed_by(self, user):
        """Check if user can access this report"""
        if user.is_superuser or hasattr(user, 'officer'):
            return True
        return self.reporter == user

    @property
    def days_since_reported(self):
        """Calculate days since report was submitted"""
        return (timezone.now() - self.date_reported).days

    def __str__(self):
        return f"{self.title} ({self.report_id})"

    class Meta:
        ordering = ['-date_reported']
        indexes = [
            models.Index(fields=['status', 'date_reported']),
            models.Index(fields=['reporter', 'date_reported']),
            models.Index(fields=['department', 'date_reported']),
        ]
        verbose_name = "Crime Report"
        verbose_name_plural = "Crime Reports"


class Notification(models.Model):
    officer = models.ForeignKey(
        'Officer',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.officer.user.username} - {self.message[:50]}"
    

# models.py - Add to your existing models
class CitizenNotification(models.Model):
    NOTIFICATION_TYPES = (
        ('status_update', 'Status Update'),
        ('reminder', 'Reminder'),
        ('general', 'General'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='general')
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_report = models.ForeignKey('CrimeReport', on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.get_full_name()}"
    

# models.py
class ReportReminder(models.Model):
    report = models.ForeignKey('CrimeReport', on_delete=models.CASCADE, related_name='reminders')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_acknowledged = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Reminder for {self.report.title} - {self.created_at}"