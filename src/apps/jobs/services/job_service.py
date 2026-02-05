from django.core.exceptions import ValidationError
from apps.jobs.models import Job
from apps.companies.models import Membership


def create_job(*, company, title, description, department, location, created_by):
    """
    Only Admin or Recruiter of company can create jobs.
    """

    if not Membership.objects.filter(
        company=company,
        user=created_by,
        role__in=[Membership.Role.ADMIN, Membership.Role.RECRUITER]
    ).exists():
        raise ValidationError("You do not have permission to create jobs for this company.")

    job = Job.objects.create(
        company=company,
        title=title,
        description=description,
        department=department,
        location=location,
        created_by=created_by
    )

    return job


def update_job(*, job, data, updated_by):
    """
    Only Admin or Recruiter can update job.
    """

    if not Membership.objects.filter(
        company=job.company,
        user=updated_by,
        role__in=[Membership.Role.ADMIN, Membership.Role.RECRUITER]
    ).exists():
        raise ValidationError("You cannot update this job.")

    for field, value in data.items():
        setattr(job, field, value)

    job.save()
    return job

