from django.core.exceptions import ValidationError
from apps.applications.models import Application
from apps.companies.models import Membership
from apps.jobs.models import Job
from django.db.models import Q
from apps.emails.services import (
    send_application_status_email,
)
from apps.emails.tasks import (
    send_application_status_email_task,
)


ALLOWED_STATUS_TRANSITIONS = {
    Application.Status.APPLIED: [
        Application.Status.SCREENING,
        Application.Status.REJECTED,
    ],
    Application.Status.SCREENING: [
        Application.Status.INTERVIEW,
        Application.Status.REJECTED,
    ],
    Application.Status.INTERVIEW: [
        Application.Status.OFFER,
        Application.Status.REJECTED,
    ],
    Application.Status.OFFER: [
        Application.Status.HIRED,
        Application.Status.REJECTED,
    ],
}



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


# TODO:(Utilize ApplicationAssignment Moodel) replace company-wide visibility with JobAssignment: any recruiter in a company can change status of all applications.
def change_application_status(*, application, status, changed_by):
    """
    Only Admin or Recruiter can change status.
    """

    if status not in Application.Status.values:
        raise ValidationError("Invalid application status.")

    if not Membership.objects.filter(
        company=application.job.company,
        user=changed_by,
        role__in=[Membership.Role.ADMIN, Membership.Role.RECRUITER]
    ).exists():
        raise ValidationError("You do not have permission to update application status.")
    
    job = application.job

    # Defensive invariant: draft jobs are frozen
    if job.status == Job.Status.DRAFT:
        raise ValidationError("Cannot modify applications for draft jobs.")
    
    current_status = application.status
    allowed_next_statuses = ALLOWED_STATUS_TRANSITIONS.get(current_status, [])

    if status not in allowed_next_statuses:
        raise ValidationError(
            f"Cannot change status from {current_status} to {status}."
        )

    application.status = status
    application.save(update_fields=["status"])

    # Email trigger (AFTER commit) - Sync for now
    send_application_status_email(
        application=application,
        to_status=status,
    )

    # ___Email Task with celery -- all set just uncomment___
    # send_application_status_email_task.delay(
    #     application_id=application.id,
    #     to_status=status,
    # )



    return application


# TODO: (Utilize ApplicationAssignment Model)replace company-wide visibility with JobAssignment: any recruiter in a company can see all applications for now.
def get_applications_for_user(*, user):
    """
    Returns:
    - Applications the user submitted (candidate)
    - Applications the user manages (recruiter/admin)
    """

    query = Q(candidate=user)

    if Membership.objects.filter(user=user).exists():
        query |= Q(job__company__memberships__user=user)

    return (
        Application.objects
        .filter(query)
        .select_related("job__company", "candidate")
        .distinct()
    )