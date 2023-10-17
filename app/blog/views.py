"""
Views for blog App.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DeleteView,
    CreateView,
    DetailView,
    UpdateView
)

from core.models import (
    Post,
    Profile
)
from .forms import PostForms


class PostListView(ListView):
    """Return a list of existing posts with status True."""
    queryset = Post.objects.filter(status=True)
    context_object_name = 'posts'
    paginate_by = 3


class PostDetailView(DetailView):
    """Return details of a post by it's pk."""
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    """Create and return a new post."""
    model = Post
    form_class = PostForms
    success_url = reverse_lazy('blog:post')

    def form_valid(self, form):
        profile = Profile.objects.get(user=self.request.user)
        form.instance.author = profile
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """Edit and return an existing post."""
    model = Post
    form_class = PostForms
    success_url = reverse_lazy('blog:post')


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """Delete an existing post by it's ID."""
    model = Post
    success_url = reverse_lazy('blog:post')

    def get(self, request, *args, **kwargs):
        """Override get method for deleting without confirmation."""
        return self.delete(request, *args, **kwargs)
