from django.contrib import messages
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.http import (
    require_http_methods,
    require_POST,
    require_safe,
)

from main import forms, models
from oscarator import settings

INTERNAL_RESET_URL_TOKEN = "confirmation"
INTERNAL_RESET_SESSION_TOKEN = "_password_reset_token"


@require_safe
def index(request):
    if not request.user.is_authenticated:
        return redirect("main:enter")
    users = User.objects.all().order_by("?")
    return render(request, "main/index.html", {"users": users})


@require_safe
def enter(request):
    if request.user.is_authenticated:
        return redirect("main:index")
    next_url = request.GET.get("next")
    return render(
        request,
        "main/enter.html",
        {"login_form": AuthenticationForm(), "next": str(next_url or "")},
    )


@require_POST
def login(request):
    form = forms.LoginForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        if not User.objects.filter(username=username).exists():
            messages.error(request, "Username does not exist.")
            return redirect("main:enter")
        password = form.cleaned_data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            dj_login(request, user)
            next_url = request.POST.get("next")
            if next_url:
                return redirect(next_url)
            else:
                return redirect("main:index")
        else:
            messages.error(request, "Invalid password.")
            return redirect("main:enter")
    return render(request, "main/enter.html")


@require_safe
def logout(request):
    if not request.user.is_authenticated:
        return redirect("main:enter")
    dj_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect(settings.LOGOUT_REDIRECT_URL)


@require_POST
def join(request):
    form = forms.JoinForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        if (
            User.objects.filter(username=username).exists()
            and User.objects.filter(email=email).exists()
        ):
            messages.error(
                request,
                "Both the username and the email are registered. <a href='/reset-password'>Reset password</a>?",
            )
            return redirect("main:enter")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username exists. Please try another.")
            return redirect("main:enter")
        if len(email) > 0 and User.objects.filter(email=email).exists():
            messages.error(
                request,
                "This email is connected to an existing account. <a href='/reset-password'>Reset password</a>?",
            )
            return redirect("main:enter")
        user = User(username=username, email=email)
        user.set_password(password)
        user.save()
        user = authenticate(request, username=username, password=password)
        dj_login(request, user)
        messages.success(request, "Welcome to Oscarator!")
        return redirect("main:index")
    else:
        messages.error(request, "Invalid submission. Please try again.")
        return redirect("main:enter")
    return render(request, "main/enter.html")


@require_http_methods(["HEAD", "GET", "POST"])
def forgot(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                from_email=settings.DEFAULT_FROM_EMAIL,
                request=request,
                email_template_name="main/password_reset_email.txt",
            )
        messages.success(request, "Password reset email sent!")
    else:
        form = PasswordResetForm()
    return render(request, "main/forgot.html", {"form": form})


@require_http_methods(["HEAD", "GET", "POST"])
def forgot_confirm(request, uidb64, token):
    if request.method == "POST":
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has changed.")
            return redirect("main:index")
        else:
            messages.error(
                request,
                "Please <span onclick='history.back(-1)' style='cursor: pointer; text-decoration: underline;'>try again</span>.",
            )
        return render(request, "main/forgot_confirm.html", {"form": form})
    else:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        validlink = False
        if user is not None:
            if token == INTERNAL_RESET_URL_TOKEN:
                session_token = request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if default_token_generator.check_token(user, session_token):
                    # If the token is valid, display the password reset form.
                    validlink = True
            else:
                if default_token_generator.check_token(user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = request.path.replace(token, INTERNAL_RESET_URL_TOKEN)
                    return HttpResponseRedirect(redirect_url)
        form = SetPasswordForm(user)
        return render(
            request, "main/forgot_confirm.html", {"form": form, "validlink": validlink}
        )


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def user(request, username):
    if request.method == "POST":
        form = forms.VoteForm(request.POST)
        if form.is_valid():
            entry_id = form.cleaned_data.get("entry")
            entry = models.Entry.objects.get(id=entry_id)
            models.Vote.objects.filter(
                entry__category=entry.category, user=request.user
            ).delete()
            models.Vote.objects.create(user=request.user, entry=entry)
            return JsonResponse(status=200, data={})
    else:
        form = forms.VoteForm()
    categories = models.Category.objects.filter(year=2019)
    user = User.objects.get(username=username)
    return render(
        request,
        "main/user.html",
        {"form": form, "categories": categories, "user": user},
    )


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def preferences(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password was successfully updated!")
            return redirect("main:index")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "main/settings.html", {"form": form})
