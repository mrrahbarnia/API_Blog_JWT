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
router.register('categories', views.CategoryModelViewSet)
router.register('tags', views.TagModelViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
