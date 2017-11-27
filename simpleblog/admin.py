from django.contrib import admin

# Register your models here.
from .models import Post, Comment, Tag

from django.db.models import Count

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = ['tag_name', 'posts_number']

    # add sorting by posts number
    def get_queryset(self, *args, **kwargs):
        """Annotate tags with number of posts"""
        return super().get_queryset(*args, **kwargs).annotate(posts_count=Count('post'))

    # add new field with tag number of posts
    def posts_number(self, obj):
        return obj.posts_count

    # make this field sortable
    posts_number.admin_order_field = 'posts_count'



class TagInline(admin.StackedInline):
    model = Tag

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ('title', 'author', 'created', 'is_public',)
    list_filter = ('is_public', )
    search_fields = ['title','author', 'text', 'tag']
    prepopulated_fields = {'slug':('title',),}

    inlines=[CommentInline]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text','post', 'author')
    list_display_links = ('post',)
    list_filter = ('post', )
