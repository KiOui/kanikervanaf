from django.shortcuts import render, redirect
from .forms import PostForm
from django.views.generic import TemplateView
from .models import Post


class PostDetailsView(TemplateView):
    """Details post page."""

    template_name = "post_details.html"

    def get(self, request, **kwargs):
        """
        GET request for post details page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the post_details page
        """
        post = Post.objects.get(id=kwargs.get("id"))
        context = {
            "post": post,
        }
        if post.author:
            context["author"] = post.author.username
        return render(request, self.template_name, context)


class PostOverviewView(TemplateView):
    """Post overview page."""

    template_name = "post_overview.html"

    def get(self, request, **kwargs):
        """
        GET request for post overview page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the post_overview page
        """
        posts = Post.objects.filter(status=1, response_to=None)
        context = {"posts": posts}

        return render(request, self.template_name, context)


class PostCreateView(TemplateView):
    """Post creation page."""

    template_name = "post_create.html"

    def get(self, request, **kwargs):
        """
        GET request for post creation page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the post_create page
        """
        form = PostForm(None)
        context = {"form": form}

        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        """
        POST request for post creation page.

        Create a Post object
        :param request: the request
        :param kwargs: keyword arguments
        :return: a redirect to the overview page or a render of the post creation page
        """
        form = PostForm(request.POST)
        context = {"form": form}

        if form.is_valid():
            user = request.user if request.user.is_authenticated else None
            title = form.cleaned_data.get("title")
            content = form.cleaned_data.get("content")
            Post.objects.create(title=title, author=user, content=content)

            return redirect("posts:post_overview")

        return render(request, self.template_name, context)
