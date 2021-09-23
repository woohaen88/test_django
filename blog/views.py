from django.shortcuts import render
from .models import Post
from django.views.generic import ListView, DetailView
# Create your views here.


class PostList(ListView):
    model = Post 
    template_name = 'blog/post_list.html'
    ordering = '-pk'

class PostDetail(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'