"""
URL's for the user API's.
"""
from django.urls import path

from .views import (
    UserRegistrationApiView,
    GenerateAuthTokenApiView,
    DestroyAuthTokenApiView,
    ChangepasswordApiView,
    CustomJwtCreateView,
    ProfileApiView,
    ActivationApiView,
    ResendActivationApiView,
    ResetPasswordRequestEmailApiView,
    ResetPasswordValidateTokenApiView,
    SetNewPasswordSerializer
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
    path('profile/',
         ProfileApiView.as_view(),
         name='profile'),
    path('activation/confirm/<str:token>/',
         ActivationApiView.as_view(),
         name='activation'),
    path('activation/resend/',
         ResendActivationApiView.as_view(),
         name='resend-activation'),
    path('reset-password/',
         ResetPasswordRequestEmailApiView.as_view(),
         name='reset-password'),
    path('reset-password/validate-token/',
         ResetPasswordValidateTokenApiView.as_view(),
         name='reset-password-validate-token'),
    path('reset-password/set-newpassword/',
         SetNewPasswordSerializer.as_view(),
         name='reset-password-confirm')
]
