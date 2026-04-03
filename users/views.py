from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages


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


@login_required
def profile_settings(request):
    return render(request, 'users/profile_settings.html')

@login_required
def profile_emailchange(request):
    if request.htmx: 
        form = EmailForm(instance=request.user)
        return render(request, 'partials/email_form.html', {'form': form})

    if request.method == "POST":
        form = EmailForm(request.POST, instance=request.user)

        if form.is_valid():
            # check if email exists
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                messages.warning(request, f'{email} is already in use.')
                return redirect('profile-settings')

    return redirect('home')