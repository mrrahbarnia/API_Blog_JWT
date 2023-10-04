"""
URL's for the user API's.
"""
from django.urls import path

from .views import (
    UserRegistrationApiView,
    GenerateAuthTokenApiView,
    ChangepasswordApiView
    )

app_name = "api-user"


urlpatterns = [
    path('registration/',
         UserRegistrationApiView.as_view(),
         name="registration"),
    path('token/',
         GenerateAuthTokenApiView.as_view(),
         name="token"),
    path('change-password/',
         ChangepasswordApiView.as_view(),
         name='change-password')
]
