from simpleblog.models import Post, Tag, Comment
from django.contrib.auth.models import User

def create_post( author=None, title="test_post_title",
                 subtitle="test_post_subtitle", text="test post text", is_public=False):
    if not author:
        author,created = User.objects.get_or_create(username="mxx", password="password")
    return Post.objects.create(author=author, title=title,
                                subtitle=subtitle, text=text, is_public=is_public)
def create_tags(*tags_list):
    tags = []
    for tag in tags_list:
        tag_object = Tag.objects.create(tag_name=tag)
        tags.append(tag_object)
    return tags

def create_user(username=None):
    if not username:
        username = "mxx"
    password="password"
    user = User.objects.create(username=username)
    user.set_password(password)
    user.save()
    return user
