from django.test import TestCase
from django.test.client import Client
from bs4 import BeautifulSoup
from .models import Post
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

    def test_post_list(self):
        self.assertEqual(2, 2)
        
        # 1.1 포스트 목록 페이지(post list)를 연다.
        response = self.client.get('/blog/')

        # 1.2 정상적으로 페이지가 로드된다.
        self.assertEqual(response.status_code, 200)

        # 1.3 페이지 타이틀에 Blog라는 문구가 있다.
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn('Blog', soup.title.text)
        
        # 1.4 NavBar
        
        self.navbar_text(soup)

        # 1.5 Blog, About Me 라는 문구가 있다.

        # 2.1 게시물이 하나도 없을 때

        self.assertEqual(Post.objects.count(), 0)
        # 2.2 메인 영역에  "아직 게시물이 없습니다"라는 문구가 나온다.
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다.', main_area.text)

        # 3.1 만약 게시물이 2개 잇다면,
        post_001 = Post.objects.create(
            title = '첫번째 포스트 입니다.',
            content = 'Hello, World, We are the World',
            author=self.user_trump)

        post_002 = Post.objects.create(
            title = '두번째 포스트 입니다.',
            content = 'Django 연습중입니다.',
            author = self.user_obama)

        self.assertEqual(Post.objects.count(), 2)

        # 3.2 포스트 목록 페이지를 새로 고침했을 때,
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')

        # 3.3 메인 영역에 포스트 2개의 타이틀이 존재한다.
        main_area = soup.find('div', id="main-area")
        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)        

        # 3.4 "아직 게시물이 없습니다"라는 문구가 없어야 한다.
        self.assertNotIn('아직 게시물이 없습니다.', main_area.text)

        self.assertIn(post_001.author.username.upper(), main_area.text)
        self.assertIn(post_002.author.username.upper(), main_area.text)

    def test_post_detail(self):
        post_001 = Post.objects.create(
            title = '첫번째 포스트 입니다.',
            content = 'Hello, World, We are the World',
            author = self.user_trump)

        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(post_001.get_absolute_url(), '/blog/1/')

        response = self.client.get(post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_text(soup)

        self.assertIn(post_001.title, soup.title.text)
        main_area = soup.find('div', id="main-area")
        post_area = main_area.find('div', id="post-area")
        self.assertIn(post_001.title, post_area.text)
        self.assertIn(self.user_trump.username.upper(), post_area.text)
        self.assertIn(post_001.content, post_area.text)