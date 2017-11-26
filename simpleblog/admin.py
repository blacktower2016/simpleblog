from django.contrib import admin

# Register your models here.
from .models import Post, Comment, Tag

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['tag_name', 'tag_posts_count']
    def tag_posts_count(self, obj):
        return obj.post_set.count()

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
