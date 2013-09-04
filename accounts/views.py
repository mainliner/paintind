from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from accounts.models import User_info
from storage_pic.models import Painting
from django import forms
from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.template.response import TemplateResponse
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
import urlparse
REDIRECT_FIELD_NAME = 'next'

def is_safe_url(url, host=None):
    """
    Return ``True`` if the url is a safe redirection (i.e. it doesn't point to
    a different host).

    Always returns ``False`` on an empty url.
    """
    if not url:
        return False
    netloc = urlparse.urlparse(url)[1]
    return not netloc or netloc == host


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'duplicate_username': ("A user with that username already exists."),
        'password_mismatch': ("The two password fields didn't match."),
    }
    username = forms.RegexField(label=("Username"), max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text = (""),
        error_messages = {
            'invalid': ("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    email = forms.RegexField(label=("Email"), max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text = (""),
        error_messages = {
            'invalid': ("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    password1 = forms.CharField(label=("Password"),
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=("Password confirmation"),
        widget=forms.PasswordInput,
        help_text = (""))

    class Meta:
        model = User
        fields = ("username",)

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

def login(request, template_name='login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():
            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
               redirect_to = settings.LOGIN_REDIRECT_URL

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    request.session.set_test_cookie()

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


def logout(request, next_page=None,
           template_name='logged_out.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           current_app=None, extra_context=None):
    """
    Logs out the user and displays 'You are logged out' message.
    """
    auth_logout(request)

    if redirect_field_name in request.REQUEST:
        next_page = request.REQUEST[redirect_field_name]
        # Security check -- don't allow redirection to a different host.
        #if not is_safe_url(url=next_page, host=request.get_host()):
        #    next_page = request.path

    if next_page:
        # Redirect to this page until the session has been cleared.
        return HttpResponseRedirect(next_page)

    current_site = get_current_site(request)
    context = {
        'site': current_site,
        'site_name': current_site.name,
        'title': ('Logged out')
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
        current_app=current_app)

@login_required()
def userhome(request):
    user = request.user
    last_painting_list = user.painting_set.all().order_by('-create_date')[:5]
    login_or_not = 1
    user_info = user.user_info_set.all()
    info = user_info[0]
    return render_to_response('mainpage.html',{'user':user,'user_info':info,'last_painting_list':last_painting_list,'login_or_not':login_or_not},context_instance=RequestContext(request))


def someone_painting(request,user_name):
    user = get_object_or_404(User, username=user_name)
    last_painting_list = user.painting_set.all().order_by("-create_date")[:5]
    login_or_not = None
    user_info = user.user_info_set.all()
    info = user_info[0]
    return render_to_response('mainpage.html',{'user':user,'user_info':info,'last_painting_list':last_painting_list,'login_or_not':login_or_not},context_instance=RequestContext(request))



def register(request):    
    if request.method == 'POST':  
        form = UserCreationForm(data=request.POST)  
        if form.is_valid():  
            new_user = User.objects.create_user(request.POST['username'], request.POST['email'], request.POST['password1'])  
            new_user.save()
            new_user.user_info_set.create(fans_num=0,follower_num=0,describe="I am new user")  
            return HttpResponseRedirect(reverse('accounts.views.userhome')) 
        else:  
            return render(request,'register.html', {'form':form})  
    else:
        form = UserCreationForm()
        return render(request,'register.html', {'form':form})


