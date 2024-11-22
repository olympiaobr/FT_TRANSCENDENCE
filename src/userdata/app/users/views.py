from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import SignupForm
from .models import Profile

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            return redirect("login")
    else:
        form = SignupForm()
    return render(request, "users/signup.html", {"form": form})

@login_required
def profile(request):
    user_profile = Profile.objects.get(user=request.user)
    return render(request, "users/profile.html", {"profile": user_profile})
