"""
Form for creating posts.
"""
from django import forms

from core.models import Post


class PostForms(forms.ModelForm):
    """Form for creating posts."""

    class Meta:
        model = Post
        fields = ['title', 'content', 'published_date']
