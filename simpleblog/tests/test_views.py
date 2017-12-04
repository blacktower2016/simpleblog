from django.test import TestCase

from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User

from simpleblog.models import Tag, Post

from django.utils.translation import activate
# Create your tests here.

from .creation_utils import create_user, create_post, create_tags

class TestPostListView(TestCase):

    def setUp(self):
        self.user = create_user()
        self.client = Client()

        self.tags = create_tags("first_tag", "second_tag", "draft_post_tag")

        self.first_public_post = create_post(author = self.user,
                                             is_public=True,
                                             subtitle="first post",
                                             text="text of first public post")
        self.first_public_post.tags.add(self.tags[0])
        self.first_public_post.save()

        self.second_public_post = create_post(author = self.user,
                                              is_public=True,
                                              subtitle="second post",
                                              text="text of second public post")
        self.second_public_post.tags.add(self.tags[1])
        self.second_public_post.save()

        self.draft_post = create_post(author = self.user,
                                      is_public=False,
                                      subtitle="draft post",
                                      text="text of first draft post")
        self.draft_post.tags.add(self.tags[2])
        self.draft_post.save()

        activate('en')

    def test_list_view_tags_filtering(self):
        response = self.client.get(reverse("simpleblog:tag-posts", args=(self.tags[0].tag_name,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.first_public_post.subtitle)
        self.assertNotContains(response, self.second_public_post.subtitle)

    def test_list_view_posts_with_not_existing_tag_are_not_shown(self):
        response = self.client.get(reverse("simpleblog:tag-posts", args=("non_existing_tag",)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No posts")

    def test_list_view_drafts_with_tag_are_not_shown_if_user_is_not_logged_in(self):
        response = self.client.get(reverse("simpleblog:tag-posts", args=(self.tags[2],)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No posts")

    def test_list_view_drafts_with_tag_are_not_shown_if_user_is_author(self):
        login = self.client.login(username=self.user.username, password="password")
        self.assertTrue(login)
        response = self.client.get(reverse("simpleblog:tag-posts", args=(self.draft_post.tags.all().first(),)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No posts")
        self.assertIn('Posts tagged with', response.context['headtitle'])

    def test_list_view_show_drafts_if_user_is_author(self):
        login = self.client.login(username=self.user.username, password="password")
        self.assertTrue(login)
        response = self.client.get(reverse("simpleblog:drafts", kwargs={'user':self.user.username, 'drafts':True}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.draft_post.subtitle)
        self.assertEqual(response.context['headtitle'], 'My drafts')

    def test_list_view_with_user_param_show_only_user_posts_and_not_drafts(self):
        response = self.client.get(reverse("simpleblog:user-posts", kwargs={'user':self.user.username}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.first_public_post.subtitle)
        self.assertContains(response, self.second_public_post.subtitle)
        self.assertNotContains(response, self.draft_post.subtitle)
        self.assertEqual(response.context['headtitle'], self.user.username+' posts')

    def test_list_view_logged_user_posts_headtitle(self):
        self.client.login(username = self.user.username, password="password")
        response = self.client.get(reverse("simpleblog:user-posts", kwargs={"user":self.user.username}))
        self.assertEqual(response.context['headtitle'], "My posts")

    def test_list_view_with_user_param_show_user_drafts(self):
        login = self.client.login(username=self.user.username, password="password")
        self.assertTrue(login)
        response = self.client.get(reverse("simpleblog:drafts", kwargs={'user':self.user.username}))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.first_public_post.subtitle)
        self.assertNotContains(response, self.second_public_post.subtitle)
        self.assertContains(response, self.draft_post.subtitle)

    def test_list_view_search_contains_only_matching_posts_and_not_drafts_if_user_not_authorized(self):
        response = self.client.get(reverse("simpleblog:home")+"?search=first")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.first_public_post.subtitle)
        self.assertNotContains(response, self.second_public_post.subtitle)
        self.assertNotContains(response, self.draft_post.subtitle)

    def test_list_view_search_contains_only_matching_posts_and_not_drafts_if_user_is_authorized(self):
        self.client.login(username=self.user.username, password="password")
        response = self.client.get(reverse("simpleblog:home")+"?search=first")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.first_public_post.subtitle)
        self.assertNotContains(response, self.second_public_post.subtitle)
        self.assertNotContains(response, self.draft_post.subtitle)
    #def test


class TestPostDetailView(TestCase):

    def setUp(self):
        self.user = create_user()
        self.client = Client()
        tags = create_tags("first_tag", "second_tag", "draft_post")
        self.draft_post = create_post(author = self.user, is_public=False)
        self.draft_post.tags.add(tags[2])
        self.draft_post.save()
        self.public_post = create_post(author = self.user, is_public=True)
        self.public_post.tags.add(tags[1])
        self.public_post.save()
        activate('en')

    def test_post_detail_view_public_post(self):
        response = self.client.get(reverse("simpleblog:view-post", kwargs={'pk':self.public_post.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.public_post.text)

    def test_post_detail_view_draft_post_is_not_shown_if_user_is_not_author(self):
        user2 = create_user(username = "mxx2")
        login = self.client.login(username=user2.username, password="password")
        response = self.client.get(reverse("simpleblog:view-post", kwargs={'pk':self.draft_post.id}))
        self.assertEqual(response.status_code, 404)

    def test_post_detail_view_draft_post_is_not_shown_if_user_not_logged_in(self):
        response = self.client.get(reverse("simpleblog:view-post", kwargs={'pk':self.draft_post.id}))
        self.assertEqual(response.status_code, 404)

    def test_post_detail_view_draft_post_is_shown_if_user_is_author(self):
        login = self.client.login(username=self.user.username, password="password")
        response = self.client.get(reverse("simpleblog:view-post", kwargs={'pk':self.draft_post.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.draft_post.text)


class TestPostCreateView(TestCase):

    def setUp(self):
        self.user=create_user()
        self.client = Client()
        activate('en')

    def test_post_create_view_if_not_logged_in_redirects_to_login_url(self):
        response = self.client.get(reverse("create-post"))
        self.assertRedirects(response, "/accounts/login/?next=/en/create/", status_code=302,  target_status_code=302)

    def test_only_logged_usercan_see_creation_form(self):
        login = self.client.login(username=self.user.username, password="password")
        self.assertTrue(login)
        response = self.client.get(reverse("create-post"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"New Post", response.content)


class TestPostUpdateView(TestCase):

    def setUp(self):
        self.user=create_user()
        self.client = Client()
        self.post = create_post(author=self.user)
        activate('en')

    def test_post_create_view_if_not_logged_in_redirects_to_login_url(self):
        response = self.client.get(reverse("update-post", args=(self.post.id,)))
        self.assertRedirects(response, "/accounts/login/?next=/en/"+str(self.post.id)+"/edit/", status_code=302,  target_status_code=302)

    def test_only_logged_usercan_see_creation_form(self):
        login = self.client.login(username=self.user.username, password="password")
        self.assertTrue(login)
        response = self.client.get(reverse("update-post", args=(self.post.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Edit Post", response.content)

class TestPostLikesToggleView(TestCase):

    def setUp(self):
        self.user=create_user()
        self.client = Client()
        self.post = create_post(author=self.user)
        activate('en')

    def test_post_likes_view_redirects_to_post_absolute_url_and_toggles_like(self):
        #user login
        url = self.post.get_absolute_url()
        login = self.client.login(username=self.user.username, password="password")
        self.assertTrue(login)
        #toggle like
        response = self.client.get(reverse("simpleblog:like-post", args=(self.post.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.post.likes.count(), 1)
        #toggle like
        response = self.client.get(reverse("simpleblog:like-post", args=(self.post.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.post.likes.count(), 0)

    def test_post_likes_view_unauthorized_user_cannot_add_like_to_posts(self):
        #toggle first like
        response = self.client.get(reverse("simpleblog:like-post", args=(self.post.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.post.likes.count(), 0)
        #toggle like
        response = self.client.get(reverse("simpleblog:like-post", args=(self.post.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.post.likes.count(), 0)


    def test_ajax_post_user_is_not_logged_id(self):

        payload = {}
        self.assertEqual(self.post.likes.count(), 0)
        response = self.client.post(reverse("simpleblog:like-post",
                args=(self.post.id,)), payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        self.assertEqual(self.post.likes.count(), 0)

    def test_ajax_post_user_is_logged_id(self):
        login = self.client.login(username=self.user.username, password="password")
        self.assertTrue(login)
        payload = {}

        # like count = 0
        self.assertEqual(self.post.likes.count(), 0)

        # click like - user likes post
        response = self.client.post(reverse("simpleblog:like-post",
                args=(self.post.id,)), payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        self.assertEqual(self.post.likes.count(), 1)

        # click like - user dislikes post
        response = self.client.post(reverse("simpleblog:like-post",
                args=(self.post.id,)), payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        self.assertEqual(self.post.likes.count(), 0)
