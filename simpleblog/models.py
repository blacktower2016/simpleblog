from django.db import models

from django.utils.translation import gettext_lazy as _
# Create your models here.
from django.urls import reverse
from django.conf import settings

from .managers import PostManager

User = settings.AUTH_USER_MODEL


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_DEFAULT,
                default=1, verbose_name=_("author"))
    title = models.CharField(max_length=50, blank=False, null=False,
                verbose_name=_("title"))
    subtitle = models.CharField(max_length=120, blank=True, null=True,
                verbose_name=_("subtitle"))
    img = models.ImageField(upload_to="blog/images/", blank=True, null=True,
                verbose_name=_("featured image"))
    text = models.TextField(blank=False, null=False, verbose_name=_("text"))
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)
    slug = models.SlugField(allow_unicode=True)
    tags = models.ManyToManyField('Tag', verbose_name=_("tags"))
    likes = models.ManyToManyField(User, blank=True, related_name='post_likes')

    objects = PostManager() # supported additional methods public() and drafts()

    def get_absolute_url(self):
        #print(self.img)
        return reverse('simpleblog:view-post', kwargs={'pk':self.id})

    def __str__(self):
        return self.title

    def tags_to_str(self):
            return ", ".join([tag.tag_name for tag in self.tags.all()])

    class Meta:
        ordering = ['-created',]


class Comment(models.Model):
    author = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    text = models.TextField(blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created',)


class Tag(models.Model):
    tag_name = models.CharField(max_length=30, blank=False, null=False, unique=True)

    def __str__(self):
        return self.tag_name
