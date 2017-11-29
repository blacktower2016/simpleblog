from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import User
from simpleblog.models import Post, Tag
from django.urls import reverse

def create_post( author=None, title="test_post_title",
                 subtitle="test_post_subtitle", text="test post text", is_public=False):
    if not author:
        author,created = User.objects.get_or_create(username="mxx",defaults = { password:"password"})
    return Post.objects.create(author=author, title=title,
                                subtitle=subtitle, text=text, is_public=is_public)
def create_tags(tags_list):
    tags = []
    for tag in tags_list:
        tag_object = Tag.objects.create(tag_name=tag)
        tags.append(tag_object)
    return tags

def create_user():
    return User.objects.create(username="mxx", password="password")

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
        tags = create_tags(("test_tag_hello", "test_tag_goodbye"))
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

    def create_tags(self, tags_list):
        tags = []
        for tag in tags_list:
            tag_object = Tag.objects.create(tag_name=tag)
            tags.append(tag_object)
        return tags

    def test_tag_str_returns_tag_name(self):
        tags = self.create_tags(("test_tag_hello", "test_tag_goodbye"))
        self.assertEqual(tags[0].__str__(), "test_tag_hello")
        self.assertEqual(tags[1].__str__(), "test_tag_goodbye")
