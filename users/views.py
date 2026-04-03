from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import ProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


# Create your views here.
def profile(request, username=None):
    if username:
        profile = get_object_or_404(User, username=username).profile
    else:
        try: 
            profile = request.user.profile
        except:
            return redirect('account_login')
    return render(request, 'users/profile.html', {"profile": profile})


@login_required
def profile_edit(request):
    form = ProfileForm(instance=request.user.profile)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid:
            form.save()
            return redirect('profile')

    if request.path == reverse('profile-onboarding'):
        onboarding = True
    else:
        onboarding = False

    return render(request, 'users/profileEdit.html', {"form": form, 'onboarding':onboarding})