from django.shortcuts import render
from .models import Post
from django.views.generic import ListView
# Create your views here.


class PostList(ListView):
    model = Post 
    template_name = 'blog/index.html'
    ordering = '-pk'

def single_post_page(request, pk):
    post = Post.objects.get(pk=pk)

    return render(request, 'blog/single_page.html', context={'post': post})
