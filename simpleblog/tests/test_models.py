from django.test import TestCase

# Create your tests here.

from .creation_utils import create_user, create_post, create_tags
from simpleblog.models import Post
from django.urls import reverse

class TestPostModel(TestCase):

    def setUp(self):
        self.user = create_user()

    def test_post_creation(self):
        post = create_post(author = self.user)
        self.assertTrue(isinstance(post, Post))
        self.assertEqual(post.__str__(), post.title)

    def test_post_absolute_url_is_reversed_simplebloghome_url(self):
        post = create_post(author = self.user)
        self.assertEqual(post.get_absolute_url(), reverse("simpleblog:view-post", args=(post.id,)))

    def test_tags_to_str_returns_comma_separated_tags_string(self):
        post = create_post(author = self.user)
        tags = create_tags("test_tag_hello", "test_tag_goodbye")
        post.tags.add(tags[0])
        post.tags.add(tags[1])
        post.save()
        self.assertIn("test_tag_hello", post.tags_to_str())
        self.assertIn("test_tag_goodbye", post.tags_to_str())
        self.assertNotIn("test_tag_morning", post.tags_to_str())
        self.assertEqual(post.tags_to_str(), "test_tag_hello, test_tag_goodbye")

    def test_post_manager_method_public_return_public_posts(self):
        public_post = create_post(author = self.user, is_public=True)
        draft_post = create_post(author = self.user, is_public=False)
        queryset = Post.objects.public()
        self.assertIn(public_post, queryset)
        self.assertNotIn(draft_post, queryset)

    def test_post_manager_method_drafts_return_draft_posts(self):
        public_post = create_post(author = self.user, is_public=True)
        draft_post = create_post(author = self.user, is_public=False)
        queryset = Post.objects.drafts()
        self.assertIn(draft_post, queryset)
        self.assertNotIn(public_post, queryset)


class TestTagModel(TestCase):

    def test_tag_str_returns_tag_name(self):
        tags = create_tags("test_tag_hello", "test_tag_goodbye")
        self.assertEqual(tags[0].__str__(), "test_tag_hello")
        self.assertEqual(tags[1].__str__(), "test_tag_goodbye")
