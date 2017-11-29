from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import User
from simpleblog.models import Post, Tag

class TestPostModel(TestCase):

    def create_post(self, author=User.objects.get(pk=1), title="test_post_title",
                     subtitle="test_post_subtitle", text="test post text"):
        return Post.objects.create(author=author, title=title,
                                    subtitle=subtitle, text=text)
    def create_tags(self, tags_list):
        tags = []
        for tag in tags_list:
            tag_object = Tag.objects.create(tag_name=tag)
            tags.append(tag_object)
        return tags


    def test_post_creation(self):
        post = self.create_post()
        self.assertTrue(isinstance(post, Post))
        self.assertEqual(post.__str__(), post.title)

    def test_post_absolute_url_is_reversed_simplebloghome_url(self):
        post = self.create_post()
        self.assertEqual(post.get_absolute_url(), "/en-us/blog/"+str(post.id)+"/")

    def test_tags_to_str_returns_comma_separated_tags_string(self):
        post = self.create_post()
        tags = self.create_tags(("test_tag_hello", "test_tag_goodbye"))
        post.tags.add(tags[0])
        post.tags.add(tags[1])
        post.save()
        self.assertIn("test_tag_hello", post.tags_to_str())
        self.assertIn("test_tag_goodbye", post.tags_to_str())
        self.assertNotIn("test_tag_morning", post.tags_to_str())
        self.assertEqual(post.tags_to_str(), "test_tag_hello, test_tag_goodbye")

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
