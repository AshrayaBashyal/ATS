from django.core.exceptions import ValidationError
from apps.applications.models import Application
from apps.companies.models import Membership


def apply_to_job(*, job, candidate, resume=None, cover_letter=None):
    """
    Candidate applies to an OPEN job.
    """

    if job.status != job.Status.OPEN:
        raise ValidationError("This job is not open for applications.")

    if Membership.objects.filter(company=job.company, user=candidate).exists():
        raise ValidationError("Company members cannot apply to their own jobs.")

    if Application.objects.filter(job=job, candidate=candidate).exists():
        raise ValidationError("You have already applied to this job.")

    application = Application.objects.create(
        job=job,
        candidate=candidate,
        resume=resume,
        cover_letter=cover_letter,
    )

    return application
