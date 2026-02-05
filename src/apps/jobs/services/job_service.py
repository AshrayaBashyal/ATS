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


def change_job_status(*, job, status, changed_by):
    """
    Only Admin or Recruiter can change status.
    """

    if not Membership.objects.filter(
        company=job.company,
        user=changed_by,
        role__in=[Membership.Role.ADMIN, Membership.Role.RECRUITER]
    ).exists():
        raise ValidationError("You cannot change job status.")

    job.status = status
    job.save(update_fields=["status"])
    return job


def delete_job(*, job, deleted_by):
    """
    Only Admin or Creator can delete jobs.
    """

    is_admin = Membership.objects.filter(
        company=job.company, 
        user=deleted_by, 
        role=Membership.Role.ADMIN
    ).exists()

    is_creator = (job.created_by == deleted_by) 
    
    if not (is_admin or is_creator):
        raise ValidationError("You do not have permission to delete this job.")

    # TODO: Consider implementing "Soft Delete" in the future.
    # Instead of job.delete(), we could set job.status = 'ARCHIVED'.
    # This prevents losing candidate application data associated with this job.
    job.delete() 




