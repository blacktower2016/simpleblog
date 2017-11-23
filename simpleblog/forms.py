from django.forms import EmailField, CharField, ModelMultipleChoiceField
from django.forms import ValidationError
from django.forms import ModelForm
from django.forms import widgets

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from simpleblog.models import Comment, Post

def username_is_not_digit(username):
    if username.isdigit():
        raise ValidationError('Username can not be entirely numeric')

class SignUpForm(UserCreationForm):
    email = EmailField(max_length=200, help_text='Required', required=True)
    username = CharField(max_length=150,
            help_text="<ul><li>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</li> \
                        <li>Your username can't be entirely numeric.</li></ul>", required=True, validators=[username_is_not_digit])

    # email should be unique
    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise ValidationError("This email already used")
        return data

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', )


class PostEditForm(ModelForm):

    tags = CharField(max_length=150, required=True)

    class Meta:
        model = Post
        fields = ('title', 'subtitle', 'img', 'text', 'tags', 'is_public')
        labels={
            'is_public':'Publish'
        }



class CommentForm(ModelForm):

    text = CharField(widget=widgets.Textarea(attrs={'rows':'5', 'placeholder':'Type your comment here...'}), label='Your comment:')

    class Meta:
        model=Comment
        fields=('text',)
