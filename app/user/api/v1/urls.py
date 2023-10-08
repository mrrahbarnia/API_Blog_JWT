"""
URL's for the user API's.
"""
from django.urls import path

from .views import (
    UserRegistrationApiView,
    GenerateAuthTokenApiView,
    DestroyAuthTokenApiView,
    ChangepasswordApiView,
    CustomJwtCreateView
    )

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)

app_name = "api-user"


urlpatterns = [
    path('registration/',
         UserRegistrationApiView.as_view(),
         name="registration"),
    path('token/login/',
         GenerateAuthTokenApiView.as_view(),
         name="token-login"),
    path('token/logout/',
         DestroyAuthTokenApiView.as_view(),
         name='token-logout'),
    path('change-password/',
         ChangepasswordApiView.as_view(),
         name='change-password'),
    path('jwt/create/',
         CustomJwtCreateView.as_view(),
         name='jwt-create'),
    path('jwt/refresh/',
         TokenRefreshView.as_view(),
         name='jwt-refresh'),
    path('jwt/verify/',
         TokenVerifyView.as_view(),
         name='jwt-verify'),
]
