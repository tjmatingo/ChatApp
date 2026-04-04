from django.urls import path
from users.views import *

urlpatterns = [
    path("", profile, name="profile"),
    path("edit/", profile_edit, name="edit-profile"),
    path("onboarding/", profile_edit, name="profile-onboarding"),
    path("settings/", profile_settings, name="profile-settings"),
    path("emailchange/", profile_emailchange, name="profile-emailchange"),
    path("emailVerify/", profile_emailVerify, name="profile-emailverify"),
    path("profiledelete/", profile_delete, name="profile-delete"),
]
