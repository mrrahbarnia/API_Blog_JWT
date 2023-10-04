"""
URL's for the user API's.
"""
from django.urls import path

from .views import (
    UserRegistrationApiView
    )

app_name = "api-user"


urlpatterns = [
    path('registration/',
         UserRegistrationApiView.as_view(),
         name="registration"),
]
