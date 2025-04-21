from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils import timezone
from datetime import timedelta
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.urls import reverse
from .forms import RegistrationForm, UserProfileForm, ProfileForm
from .models import Profile
from campaigns.models import Campaign
from transactions.models import Transaction
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.views.decorators.http import require_http_methods

User = get_user_model()


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data["email"]

            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                if not user.is_active:
                    return handle_existing_user(request, user)
                messages.error(request, "Email already registered")
                return render(request, "account/register.html", {"form": form})

            try:
                user = create_user(form)
                create_user_profile(user, form)
                send_activation_email(request, user)
                messages.info(request, "Activation link sent to your email")
                return redirect("activation_email")
            except Exception as e:
                handle_error(request, e, form)

        return render(request, "account/register.html", {"form": form})

    form = RegistrationForm()
    return render(request, "account/register.html", {"form": form})


def create_user(form):
    return User.objects.create_user(
        username=form.cleaned_data["email"],
        email=form.cleaned_data["email"],
        password=form.cleaned_data["password1"],
        first_name=form.cleaned_data["first_name"],
        last_name=form.cleaned_data["last_name"],
        is_active=False,
    )


def create_user_profile(user, form):
    Profile.objects.get_or_create(
        user=user,
        defaults={
            "mobile_phone": form.cleaned_data["mobile_phone"],
            "profile_picture": form.cleaned_data["profile_picture"],
        },
    )


def send_activation_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    activation_url = request.build_absolute_uri(
        reverse("activate_intermediate") + f"?uidb64={uid}&token={token}"
    )

    subject = "Activate Your Account"
    message = render_to_string(
        "account/activation_email.html",
        {
            "user": user,
            "activation_url": activation_url,
        },
    )
    send_mail(
        subject,
        "",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=message,
        fail_silently=False,
    )


def handle_existing_user(request, user):
    if user.is_active:
        messages.error(request, "Email already registered")
        return redirect("register")

    send_activation_email(request, user)
    messages.info(request, "New activation link sent to your email")
    return redirect("activation_email")


def handle_error(request, error, form):
    messages.error(request, f"Error: {str(error)}")
    return render(request, "account/register.html", {"form": form})


def activate_intermediate(request):
    uidb64 = request.GET.get("uidb64")
    token = request.GET.get("token")
    return render(
        request,
        "account/activate_intermediate.html",
        {"uidb64": uidb64, "token": token},
    )


@require_http_methods(["GET", "POST"])
def activate(request):
    uidb64 = request.GET.get("uidb64") or request.POST.get("uidb64")  # يعمل مع GET/POST
    token = request.GET.get("token") or request.POST.get("token")

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if user.is_active:
            messages.error(request, "Account is already activated!")
            return redirect("login")

        if (timezone.now() - user.date_joined) > timedelta(hours=24):
            messages.error(request, "Activation link expired")
            return redirect("register")

        user.is_active = True
        user.save()
        messages.success(request, "Account activated successfully!")
        return redirect("login")
    else:
        messages.error(request, "Invalid activation link!")
        return redirect("register")


def activation_email(request):
    return render(request, "account/check_email.html")


def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect("profile")
            messages.error(request, "Account not activated")
            return redirect("register")

        messages.error(request, "Invalid credentials")
        return redirect("login")

    return render(request, 'account/profile_login.html')
      

@login_required
def profile_view(request):
    profile = request.user.profile
    return render(request, "account/profile.html", {"profile": profile})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')  # Redirect to the profile page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserProfileForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    return render(request, 'account/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def delete_account(request):
    if request.method == "POST":
        request.user.delete()
        logout(request)
        messages.success(request, "Your account has been deleted successfully.")
        return redirect("home")  # Redirect to the home page after deletion
    return render(request, "account/delete_account.html")


def user_logout(request):
    logout(request)
    return redirect("login")
