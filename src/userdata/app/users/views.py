import logging
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.shortcuts import render, redirect
from .forms import SignupForm
from .models import Profile

logger = logging.getLogger(__name__)

def signup(request):
    logger.debug("Signup view accessed")
    if request.method == "POST":
        logger.debug("POST data: %s", request.POST)
        form = SignupForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data["password"])  # Hash the password
                user.save()  # Save the user instance

                # Ensure a unique display_name
                random_suffix = get_random_string(5)  # Generate a random string of 5 characters
                display_name = f"{user.username}_{random_suffix}"

                # Create a Profile for the user
                Profile.objects.create(user=user, display_name=display_name)

                logger.info("User %s created successfully", user.username)

                login(request, user)  # Log the user in immediately
                return redirect("profile")  # Redirect to profile page
            except Exception as e:
                logger.error("Error during user creation: %s", e)
                form.add_error(None, "An unexpected error occurred. Please try again.")
        else:
            logger.warning("Invalid form submission: %s", form.errors)
    else:
        form = SignupForm()
    return render(request, "users/signup.html", {"form": form})

@login_required
def profile(request):
    logger.debug("Profile view accessed by user: %s", request.user)
    try:
        user_profile = Profile.objects.get(user=request.user)
        logger.debug("Profile loaded: %s", user_profile)
    except Profile.DoesNotExist:
        logger.error("Profile not found for user: %s", request.user)
        return redirect("signup")
    return render(request, "users/profile.html", {"profile": user_profile})
