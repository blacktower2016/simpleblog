from django.shortcuts import render,  redirect, get_object_or_404
from django.http import Http404, HttpResponse

# Create your views here.

from .models import Post, Tag
from django.views.generic import CreateView, DetailView, ListView, UpdateView, RedirectView
from django.views.generic import DayArchiveView, View, TemplateView
from django.views.generic.edit import FormMixin, ProcessFormView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import Q

from .forms import SignUpForm, CommentForm, PostEditForm

from django.conf import settings
from django.urls import reverse, reverse_lazy, resolve

from django.utils.text import slugify
from django.utils.html import strip_tags

from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login, get_user_model
from django.template.loader import render_to_string

import bleach
from cfe.helpers.bleach_whitelist import summernote_tags, summernote_attrs, protocols

class NewUserView(CreateView):
    form_class=SignUpForm
    template_name='simpleblog/post_form.html'
    model = settings.AUTH_USER_MODEL
    success_url = reverse_lazy('simpleblog:home')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(reverse('simpleblog:home'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form_title'] = 'New User Registration'
        return context

    def form_valid(self, form):
        # Send email with profile activation link
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        to_email = form.cleaned_data.get('email')

        self.send_activation_email(user, to_email)

        return render(self.request,'simpleblog/messages.html',
                        {'message':{
                            'title':'New user email confirmation',
                            'body':'Please check your email to complete the registration.'
                            }})

    def send_activation_email(self, user, to_email):
        token = default_token_generator.make_token(user)
        current_site = get_current_site(self.request)
        #activation_link = "{0}{1}".format(current_site, reverse("simpleblog:activate", kwargs={ 'user_id':user.id, 'token':token} ))
        email_message = render_to_string('simpleblog/email_acc_activation.html', {
                'user':user,
                'domain':current_site.domain,
                'user_id': user.id,
                'token': token
            })
        mail_subject = 'Activate your SimpleBlog account.'
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

        return render(self.request,'simpleblog/messages.html',
                        {'message':{
                            'title':'Activation failed',
                            'body':'Please try again'
                            }
                        })


class PostListView(ListView):
    model = Post
    paginate_by = 5

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['headtitle'] = self.headtitle
        return context

    def get_queryset(self):
        print(self.kwargs)
        user = self.kwargs.get('user')
        query = self.request.GET.get('search')
        tag = self.kwargs.get('tag')

        self.headtitle='Latest posts'

        # only published posts
        # methods public() and drafts() are defned in Post model manager PostManager
        queryset = Post.objects.public()

        # posts filtered by tag
        if tag:
            # filter does not return DoesNotExist exception, but None
            tag_object = Tag.objects.filter(tag_name=tag.lower()).first()
            if not tag_object:
                return queryset.none()
            queryset = tag_object.post_set.all().public()
            self.headtitle = 'Posts tagged with "{}"'.format(tag)

        #posts filtered by user
        if user:
            self.headtitle='{} posts'.format(user)
            if user == self.request.user.username:
                if self.kwargs.get('drafts'):
                    self.headtitle='My drafts'
                    return Post.objects.filter(author__username=user).drafts()
                self.headtitle='My posts'
            queryset = queryset.filter(author__username=user)

        # searching in posts
        if query and len(query)>=3:
            queryset = queryset.filter( Q(title__icontains=query)|
                                        Q(text__icontains=query) |
                                        Q(author__username__icontains=query)|
                                        Q(subtitle__icontains=query)|
                                        Q(tags__tag_name__iexact=query)).distinct()
            self.headtitle='Searching results: "{}"'.format(query)
        return queryset



class PostDetailView(DetailView, FormMixin, ProcessFormView):
    model = Post
    form_class = CommentForm

    def get_object(self):
        # if post is draft and user is not the author : error 404
        post = super().get_object()
        if (post.is_public == False) and (self.request.user != post.author):
            raise Http404("No post found matching the query")
        return post

    # after commenting return to this very page
    def get_success_url(self):
        return reverse('simpleblog:view-post',kwargs={'pk':self.get_object().id})

    # comments form
    def form_valid(self, form):
        form.instance.text = bleach.clean(
                                form.instance.text,
                                tags=summernote_tags,
                                attributes=summernote_attrs,
                                protocols=protocols
                            ).strip()
        form.instance.author = self.request.user
        form.instance.post = self.get_object()

        # save form and return to this very page
        form.save()
        return redirect(self.get_success_url()+"#last_comment")


class PostCreateView(CreateView, LoginRequiredMixin):
    model = Post
    form_class=PostEditForm
    #fields = ['title', 'subtitle', 'img', 'text', 'is_public','tags']

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form_title'] = 'New Post'
        return context

    # post creating form
    def form_valid(self,form):
        form.instance.slug = slugify(form.instance.title, allow_unicode=True)
        form.instance.text = bleach.clean(
                                    form.instance.text,
                                    tags=summernote_tags,
                                    attributes=summernote_attrs,
                                    protocols=protocols
                            ).strip()
        form.instance.author = self.request.user
        # tags from string will be saved to m2m post.tags field
        tags = strip_tags(form.cleaned_data['tags']).split(", ")
        form.cleaned_data['tags'] = [Tag.objects.get_or_create(tag_name=tag.lower())[0] for tag in tags]

        return super().form_valid(form)


class PostUpdateView(UpdateView, LoginRequiredMixin):
    model = Post
    template_name = 'simpleblog/post_form.html'
    form_class=PostEditForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form_title'] = 'Edit Post'
        return context

    # prepopulate tags field in form with string of tags, separated by comma
    def get_initial(self, *args, **kwargs):
        initial = super().get_initial(*args, **kwargs)
        initial['tags'] = self.object.tags_to_str()
        return initial

    def form_valid(self,form):

        # tags from string will be saved to m2m post.tags field
        tags = strip_tags(form.cleaned_data['tags']).split(", ")
        form.cleaned_data['tags'] = [Tag.objects.get_or_create(tag_name=tag.lower())[0] for tag in tags]
        # filter html tags
        form.instance.text = bleach.clean(
                                    form.instance.text,
                                    tags=summernote_tags,
                                    attributes=summernote_attrs,
                                    protocols=protocols
                            ).strip()
        return super().form_valid(form)


class PostLikesToggleView(RedirectView, LoginRequiredMixin):
    """
    Toggle post likes
    """
    pattern_name = 'simpleblog:view-post'

    def get_redirect_url(self, *args, **kwargs):

        post = get_object_or_404(Post, pk=kwargs['pk'])
        if self.request.user.is_authenticated:
            if self.request.user in post.likes.all():
                post.likes.remove(self.request.user)
            else:
                post.likes.add(self.request.user)
        return super().get_redirect_url(*args, **kwargs)


class PostsByDateView(DayArchiveView):
    model = Post
    month_format = '%m'
    date_field = 'created'
    template_name = "simpleblog/post_list.html"
    paginate_by = 5
