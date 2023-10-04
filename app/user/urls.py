"""
URL's for user app.
"""
from django.urls import path, include


app_name = "user"


urlpatterns = [
    path('api/v1/', include("user.api.v1.urls")),
]
