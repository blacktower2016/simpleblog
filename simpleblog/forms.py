from django.forms import CharField #, EmailField, ModelMultipleChoiceField
# from django.forms import ValidationError
from django.forms import ModelForm
from django.forms import widgets

# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User

from django.utils.translation import gettext_lazy as _

from simpleblog.models import Comment, Post


class PostEditForm(ModelForm):

    tags = CharField(max_length=150, required=True, label=_("Tags"))

    class Meta:
        model = Post
        fields = ('title', 'subtitle', 'img', 'text', 'tags', 'is_public')
        labels={
            'is_public':_('Publish'),
        }



class CommentForm(ModelForm):

    text = CharField(widget=widgets.Textarea(attrs={'rows':'5', 'placeholder':_('Type your comment here...')}), label='Your comment:')

    class Meta:
        model=Comment
        fields=('text',)
