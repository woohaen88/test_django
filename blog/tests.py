from unittest.main import main
from django.test import TestCase
from django.test.client import Client
from bs4 import BeautifulSoup
from .models import Category, Post
from django.contrib.auth.models import User

# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(
            username = 'trump',
            password = 'somepassword'
        )
        self.user_obama = User.objects.create_user(
            username = 'obama',
            password = 'somepassword'
        )

        self.category_programming = Category.objects.create(
            name = 'programming', slug='programming'
        )

        self.category_music = Category.objects.create(
            name = 'music', slug='music'
        )

        self.post_001 = Post.objects.create(
            title = '첫번째 포스트 입니다.',
            content = 'Hello, World, We are the World',
            category = self.category_programming,
            author=self.user_trump)

        self.post_002 = Post.objects.create(
            title = '두번째 포스트 입니다.',
            content = 'Django 연습중입니다.',
            category = self.category_music,
            author = self.user_obama)

        self.post_003 = Post.objects.create(
            title = '세번째 포스트 입니다.',
            content = '카테고리가 없을수도 있죠',
            author = self.user_obama)

    def navbar_text(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo_btn = navbar.find('a', text="Do It Django")
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text="Home")
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text="Blog")
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text="About Me")
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_programming} ({self.category_programming.post_set.count()})',
        categories_card.text)
        self.assertIn(f'{self.category_music} ({self.category_music.post_set.count()})',
        categories_card.text)
        self.assertIn(
            f'미분류 ({Post.objects.filter(category=None).count()})',
            categories_card.text
        )

    def test_post_list_with_posts(self):
        self.assertEqual(Post.objects.count(), 3)
        
        response = self.client.get('/blog/')        
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_text(soup)
        self.category_card_test(soup)
        self.assertIn('Blog', soup.title.text)

        main_area = soup.find('div', id="main-area")
        self.assertNotIn('아직 게시물이 없습니다.', main_area.text)

        post_001_card = main_area.find('div', id='post-1')        
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)        
        self.assertIn(self.post_002.category.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn(self.post_003.title, post_003_card.text)        
        self.assertIn('미분류', post_003_card.text)

        

        self.assertIn(self.post_001.author.username.upper(), main_area.text)
        self.assertIn(self.post_002.author.username.upper(), main_area.text)
    
    def test_post_list_without_posts(self):
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_text(soup)        
        self.assertIn('Blog', soup.title.text)
        
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다.', main_area.text)

    def test_post_detail(self):
        self.assertEqual(Post.objects.count(), 3)
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_text(soup)

        self.assertIn(self.post_001.title, soup.title.text)
        main_area = soup.find('div', id="main-area")
        post_area = main_area.find('div', id="post-area")
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.user_trump.username.upper(), post_area.text)
        self.assertIn(self.post_001.content, post_area.text)