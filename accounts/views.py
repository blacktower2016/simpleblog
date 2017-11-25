from django.shortcuts import render, redirect
from django.urls import reverse_lazy

# Create your views here.
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login, get_user_model
from django.template.loader import render_to_string
from .forms import SignUpForm

from django.views.generic import CreateView, View

from django.utils.translation import gettext as _

class NewUserView(CreateView):
    form_class=SignUpForm
    template_name='accounts/registration.html'
    model = settings.AUTH_USER_MODEL
    success_url = reverse_lazy('simpleblog:home')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(reverse('simpleblog:home'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form_title'] = _('New User Registration')
        return context

    def form_valid(self, form):
        # Send email with profile activation link
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        to_email = form.cleaned_data.get('email')

        self.send_activation_email(user, to_email)

        return render(self.request,'accounts/messages.html',
                        {'message':{
                            'title':_('New user email confirmation'),
                            'body': _('Please check your email to complete the registration.')
                            }})

    def send_activation_email(self, user, to_email):
        token = default_token_generator.make_token(user)
        current_site = get_current_site(self.request)
        #activation_link = "{0}{1}".format(current_site, reverse("simpleblog:activate", kwargs={ 'user_id':user.id, 'token':token} ))
        email_message = render_to_string('accounts/email_acc_activation.html', {
                'user':user,
                'domain':current_site.domain,
                'user_id': user.id,
                'token': token
            })
        mail_subject = _('Activate your SimpleBlog account.')
        email = EmailMessage(mail_subject, email_message, to=[to_email])
        email.send()


class ActivateView(View):

    def get(self, request, user_id, token):
        if user_id:
            User = get_user_model()
            user = User.objects.get(pk=user_id)

            if user and not user.is_active \
                and default_token_generator.check_token(user, token):
                    user.is_active = True
                    user.save()
                    login(self.request, user)
                    return redirect(reverse("simpleblog:home"))

        return render(self.request,'accounts/messages.html',
                        {'message':{
                            'title':_('Activation failed'),
                            'body':_('Please try again')
                            }
                        })
