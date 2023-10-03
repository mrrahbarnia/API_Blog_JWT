"""
Abstract model for using in different models.
"""
from django.db import models


class TimeStampedModel(models.Model):
    """Created_at and Updated_at which must be in every models."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
