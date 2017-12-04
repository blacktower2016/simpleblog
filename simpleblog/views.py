from django.shortcuts import render,  redirect, get_object_or_404
from django.http import Http404

# Create your views here.

from .models import Post, Tag
from django.views.generic import CreateView, DetailView, ListView, UpdateView, RedirectView
from django.views.generic import DayArchiveView#, View, TemplateView
from django.views.generic.edit import FormMixin, ProcessFormView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import Q

from .forms import CommentForm, PostEditForm #, SignUpForm

from django.urls import reverse#, reverse_lazy, resolve

from django.utils.text import slugify
from django.utils.html import strip_tags

import bleach
from cfe.helpers.bleach_whitelist import summernote_tags, summernote_attrs, protocols

from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy


class PostListView(ListView):
    model = Post
    paginate_by = 5

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['headtitle'] = self.headtitle
        return context

    def get_queryset(self):
        """
        Filter objects by tag, by user or by search string and add
        appropriate "headtitle" param to the context
        """
        #print(self.kwargs)
        user = self.kwargs.get('user')
        query = self.request.GET.get('search')
        tag = self.kwargs.get('tag')

        self.headtitle=_('Latest posts')

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
            self.headtitle = _('Posts tagged with "{tag}"').format(tag=tag)

        #posts filtered by user
        if user:
            self.headtitle='{} posts'.format(user)
            if user == self.request.user.username:
                if self.kwargs.get('drafts'):
                    self.headtitle=_('My drafts')
                    return Post.objects.filter(author__username=user).drafts()
                self.headtitle=_('My posts')
            queryset = queryset.filter(author__username=user)

        # searching in posts
        if query and len(query)>=3:
            queryset = queryset.filter( Q(title__icontains=query)|
                                        Q(text__icontains=query) |
                                        Q(author__username__icontains=query)|
                                        Q(subtitle__icontains=query)|
                                        Q(tags__tag_name__iexact=query)).distinct()
            self.headtitle=_('Searching results: "{}"').format(query)
        return queryset


from django.contrib import messages
class PostDetailView(DetailView, FormMixin, ProcessFormView):
    model = Post
    form_class = CommentForm

    def get_object(self, *args, **kwargs):
        # if post is draft and user is not the author : error 404
        post = super().get_object(*args, **kwargs)
        if (post.is_public == False) and (self.request.user != post.author):
            raise Http404(_("No post found matching the query"))
        return post

    # after commenting return to this very page
    def get_success_url(self):
        return reverse('simpleblog:view-post',kwargs={'pk':self.get_object().id})

    # comments form
    def form_valid(self, form):
        form.instance.text = ''.join(bleach.clean(
                                form.instance.text,
                                tags=summernote_tags,
                                attributes=summernote_attrs,
                                protocols=protocols
                            ).strip().split('<p><br></p>'))
        form.instance.author = self.request.user
        form.instance.post = self.get_object()

        # save form and return to this very page
        form.save()
        messages.success(self.request, _("Your comment has been added successfully."))
        return redirect(self.get_success_url()+"#last_comment")


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class=PostEditForm
    #fields = ['title', 'subtitle', 'img', 'text', 'is_public','tags']

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form_title'] = _('New Post')
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


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'simpleblog/post_form.html'
    form_class=PostEditForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form_title'] = _('Edit Post')
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

from django.http import JsonResponse
class PostLikesToggleView(RedirectView, LoginRequiredMixin):
    """
    Toggle post likes
    """
    pattern_name = 'simpleblog:view-post'

    def post(self, *args, **kwargs):
        """ Toggle likes with ajax """
        data = {}
        post = get_object_or_404(Post, pk=kwargs['pk'])
        if self.request.is_ajax():
            if self.request.user.is_authenticated:
                data['user'] = True;
                if self.request.user in post.likes.all():
                    post.likes.remove(self.request.user)
                else:
                    post.likes.add(self.request.user)
                data['likes'] = post.likes.count()
            else:
                data['errors'] = _("You must login to rate the posts.")
        return JsonResponse(data)


    def get_redirect_url(self, *args, **kwargs):
        """toggle likes without ajax"""
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
