from django.urls import path
from .views import *

urlpatterns = [
    path("create/", CompanyCreateView.as_view()),
    path("mine/", MyCompaniesView.as_view()),
    path("<int:company_id>/members/", CompanyMembersView.as_view()),
    path("<int:company_id>/invite/", SendInviteView.as_view()),
    path("invite/<int:invite_id>/accept/", AcceptInviteView.as_view()),
    path("invite/<int:invite_id>/reject/", RejectInviteView.as_view()),
    path("membership/<int:membership_id>/role/", ChangeRoleView.as_view()),
    path("membership/<int:membership_id>/remove/", RemoveMemberView.as_view()),
]
