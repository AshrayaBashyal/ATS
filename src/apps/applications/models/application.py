from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from apps.jobs.models import Job


class Application(models.Model):

    class Status(models.TextChoices):
        APPLIED = "applied", "Applied"
        SCREENING = "screening", "Screening"
        INTERVIEW = "interview", "Interview"
        OFFER = "offer", "Offer"
        REJECTED = "rejected", "Rejected"
        HIRED = "hired", "Hired"

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.APPLIED
    )

    resume = models.FileField(
        upload_to="resumes/", 
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'doc', 'txt'])],
        blank=False, 
        null=False,
        help_text="Required: PDF or Word format."
    )
    
    cover_letter = models.FileField(
        upload_to="cover_letters/", 
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'doc', 'txt'])],
        blank=True, 
        null=True,
        help_text="Optional: PDF or Word format."
    )


    class Meta:
        unique_together = ["job", "candidate"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.candidate.email} → {self.job.title}"


