from django.shortcuts import render
# accounts/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from allauth.account.models import EmailAddress
from django.contrib import messages
from allauth.account.models import EmailAddress
from allauth.account.utils import perform_login
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from .forms import ProfileForm
from django.contrib.auth import update_session_auth_hash,logout


def terms_view(request):
    return render(request, 'accounts/terms.html')




def resend_email_verification(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                email_address = EmailAddress.objects.get(email=email, verified=False)
                email_address.send_confirmation(request)
                messages.success(request, "Verification email has been resent!")
            except EmailAddress.DoesNotExist:
                messages.error(request, "Email not found or already verified.")
        else:
            messages.error(request, "Please provide an email.")
    return redirect('account_login')  # Redirect to login or wherever





@login_required
def profile_dashboard(request):
    user = request.user
    
    # Check if user has a usable password
    if not user.has_usable_password():
        password_form = SetPasswordForm(user)
        is_social_only = True
    else:
        password_form = PasswordChangeForm(user)
        is_social_only = False

    # Profile edit form
    if request.method == 'POST' and 'username' in request.POST:
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile_dashboard')
    else:
        form = ProfileForm(instance=user)

    # Handle password change or set password form submission
    if request.method == 'POST' and ('old_password' in request.POST or 'new_password1' in request.POST):
        if is_social_only:
            password_form = SetPasswordForm(user, request.POST)
        else:
            password_form = PasswordChangeForm(user, request.POST)
        if password_form.is_valid():
            password_form.save()
            #update_session_auth_hash(request, user)
            logout(request)
            messages.success(request, 'Password updated successfully.')
            return redirect('profile_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'accounts/profile_dashboard.html', {
        'form': form,
        'user': user,
        'password_form': password_form,
        'is_social_only': is_social_only,
    })
    
