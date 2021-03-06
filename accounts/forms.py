from django.forms import EmailField, CharField
from django.forms import ValidationError
from django.forms import ModelForm

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from simpleblog.models import Comment, Post

from django.utils.translation import gettext as _, gettext_lazy

def username_is_not_numeric(username):
    if username.isdigit():
        raise ValidationError(_('Username can not be entirely numeric'))

class SignUpForm(UserCreationForm):
    email = EmailField(max_length=200, help_text=gettext_lazy('Required'), required=True)
    username = CharField(max_length=150,
            help_text=gettext_lazy("<ul><li>Required. 150 characters or fewer. \
                        Letters, digits and @/./+/-/_ only.</li> \
                        <li>Your username can't be entirely numeric.</li></ul>"),
                         required=True, validators=[username_is_not_numeric], label=gettext_lazy("Username"))

    # email should be unique
    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise ValidationError(_("This email already used"))
        return data

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', )
