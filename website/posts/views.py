from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from .forms import PostForm
from django.views.generic import TemplateView
from .models import Post


class PostDetailsView(TemplateView):
    """Details posts page."""

    template_name = "posts/post_details.html"
    paginate_by = 50

    def get(self, request, **kwargs):
        """
        GET request for posts details page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the post_details page
        """
        post = kwargs.get('post')
        reactions = Post.objects.filter(response_to=post, status=1)
        page = kwargs.get('page')
        paginator = Paginator(reactions, self.paginate_by)
        context = {
            "post": post,
            "page": paginator.get_page(page),
            "form": PostForm()
        }
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        """
        POST request for post details page.

        Create a Post object
        :param request: the request
        :param kwargs: keyword arguments
        :return: a redirect to the overview page or a render of the posts creation page
        """
        post = kwargs.get('post')
        reactions = Post.objects.filter(response_to=post, status=1)
        page = kwargs.get('page')
        paginator = Paginator(reactions, self.paginate_by)
        form = PostForm(request.POST)

        if form.is_valid():
            user = request.user if request.user.is_authenticated else None
            title = form.cleaned_data.get("title")
            content = form.cleaned_data.get("content")
            Post.objects.create(title=title, author=user, content=content, response_to=post)
            form = PostForm()

        context = {
            "post": post,
            "page": paginator.get_page(page),
            "form": form
        }

        return render(request, self.template_name, context)


class PostOverviewView(TemplateView):
    """Post overview page."""

    template_name = "posts/post_overview.html"
    paginate_by = 50

    def get(self, request, **kwargs):
        """
        GET request for posts overview page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the post_overview page
        """
        posts = Post.objects.filter(status=1, response_to=None)
        page = kwargs.get('page')
        paginator = Paginator(posts, self.paginate_by)
        context = {"page": paginator.get_page(page)}

        return render(request, self.template_name, context)


class PostCreateView(TemplateView):
    """Post creation page."""

    template_name = "posts/post_create.html"

    def get(self, request, **kwargs):
        """
        GET request for posts creation page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the post_create page
        """
        form = PostForm(None)
        context = {"form": form}

        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        """
        POST request for posts creation page.

        Create a Post object
        :param request: the request
        :param kwargs: keyword arguments
        :return: a redirect to the overview page or a render of the posts creation page
        """
        form = PostForm(request.POST)
        context = {"form": form}

        if form.is_valid():
            user = request.user if request.user.is_authenticated else None
            title = form.cleaned_data.get("title")
            content = form.cleaned_data.get("content")
            Post.objects.create(title=title, author=user, content=content)

            return redirect("posts:post_overview", page=1)

        return render(request, self.template_name, context)


class PostUserOverview(LoginRequiredMixin, TemplateView):

    template_name = "posts/post_user_overview.html"
    paginate_by = 50

    def get(self, request, **kwargs):
        """
        GET request for user posts details page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the post_details page
        """
        posts = Post.objects.filter(author=request.user, response_to=None)
        page = kwargs.get('page')
        paginator = Paginator(posts, self.paginate_by)
        context = {
            "page": paginator.get_page(page),
        }
        return render(request, self.template_name, context)

