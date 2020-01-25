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

    # find if user has voted for all categories
    user_vote_complete = (
        models.Vote.objects.filter(user=request.user, entry__year=2020).count()
        == models.Vote.objects.all().count()
    )

    # build all users' entries dict
    all_users_entries = {}
    users = User.objects.all().order_by("?")
    for u in users:
        all_users_entries[u.username] = []
    votes = models.Vote.objects.filter(entry__year=2020)
    for v in votes:
        all_users_entries[v.user.username].append(v.entry)

    # calculate all users successful predictions
    # user_wins_dict = {}
    # for u in users:
    #     user_wins_dict[u.username] = 0
    # for u in users:
    #     votes = models.Vote.objects.filter(user=u)
    #     for v in votes:
    #         if v.entry.is_winner:
    #             user_wins_dict[u.username] += 1

    user_wins = []
    # values = user_wins_dict.values()
    # lim = len(values)
    # values_de = list(values)
    # for i in range(lim):
    #     for k, v in user_wins_dict.items():

    #         # find max
    #         max_value = max(values_de)

    #         if max_value == v:
    #             user_wins.append({k: v})
    #             values_de[values_de.index(max_value)] = 0

    # for i in user_wins:
    #     key = list(i.keys())[0]
    #     if i[key] == 0:
    #         del i[key]

    return render(
        request,
        "main/index.html",
        {
            "users": users,
            "user_wins": user_wins,
            "all_users_entries": all_users_entries,
            "user_vote_complete": user_vote_complete,
        },
    )


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
        return JsonResponse(status=400, data={})
        # form = forms.VoteForm(request.POST)
        # if form.is_valid():
        #     entry_id = form.cleaned_data.get("entry")
        #     entry = models.Entry.objects.get(id=entry_id)
        #     models.Vote.objects.filter(
        #         entry__category=entry.category, user=request.user
        #     ).delete()
        #     models.Vote.objects.create(user=request.user, entry=entry)
        #     return JsonResponse(status=200, data={})
    else:
        form = forms.VoteForm()

    # build this user's votes dict
    categories = models.Category.objects.all()
    entries = models.Entry.objects.filter(year=2020)
    user = User.objects.get(username=username)
    user_votes = {}
    for c in categories:
        user_votes[c.name] = []
    for e in entries:
        if e.year == 2020:
            user_votes[e.category.name].append(e)

    # calculate user successful predictions
    user_wins = 0
    # for c in categories:
    #     for e in c.entry_set.all():
    #         for v in e.vote_set.all():
    #             if v.user == user and v.entry == e and v.entry.is_winner:
    #                 user_wins += 1

    return render(
        request,
        "main/user.html",
        {
            "form": form,
            "categories": categories,
            "user": user,
            "user_wins": user_wins,
            "user_votes": user_votes,
        },
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
