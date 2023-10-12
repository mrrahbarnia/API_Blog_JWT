"""
Blog API's URL's.
"""
from django.urls import (
    path,
    include
)

from rest_framework import routers

from blog.api.v1 import views

app_name = 'api-blog'

router = routers.DefaultRouter()
router.register('posts', views.PostModelViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
