from apps.companies.models import Company, Membership


def create_company(*, name, description, created_by):
    """
    Creates a company and assigns creator as ADMIN.
    """
    company = Company.objects.create(
        name=name,
        description=description,
        created_by=created_by
    )

    Membership.objects.create(
        user=created_by,
        company=company,
        role=Membership.Role.ADMIN
    )

    return company
