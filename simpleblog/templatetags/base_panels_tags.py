from simpleblog.models import Post, Tag, Comment
from django import template
from django.db.models import Count
from datetime import date
from django.db.models import Q

register = template.Library()

@register.assignment_tag
def get_recent_posts():
    return Post.objects.filter(is_public=True).order_by('-created')[:5]

@register.assignment_tag
def get_tags():
    return Tag.objects.filter(post__is_public=True).annotate(posts_number=Count('post')).order_by('-posts_number')[:10]

@register.assignment_tag
def get_recent_comments():
    return Comment.objects.filter(post__is_public=True).order_by('-created')[:5]


MODEL = Post
DATE_FIELD = 'created'
URL_NAME = 'simpleblog:calendar'
ADDITIONAL_FILTERS = {'is_public':True}
# url should have <year> <month> and <day> parameters
day_abbr = ['Mo','Tu','We','Th','Fr','Sa','Su']

@register.simple_tag
def print_month_calendar():
    from simpleblog.helpers.blog_calendar import BlogCalendar
    b = BlogCalendar(MODEL, DATE_FIELD, URL_NAME, additional_filters=ADDITIONAL_FILTERS, day_abbreviations=day_abbr)
    current_date = date.today()
    return b.formatmonth(current_date.year, current_date.month)
