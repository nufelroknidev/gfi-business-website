from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Post


def news_list(request):
    posts = Post.objects.filter(is_published=True)
    paginator = Paginator(posts, 9)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'news/list.html', {'page_obj': page_obj})


def news_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    return render(request, 'news/detail.html', {'post': post})
