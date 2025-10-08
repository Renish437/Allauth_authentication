from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from .models import CustomProfiles

# Email verification check
def is_verified(user):
    try:
        email = EmailAddress.objects.get(user=user, primary=True)
        return email.verified
    except EmailAddress.DoesNotExist:
        return False
is_verified.boolean = True
is_verified.short_description = "Verified Email"

# Third-party login check
def is_social(user):
    return SocialAccount.objects.filter(user=user).exists()
is_social.boolean = True
is_social.short_description = "Third-Party Login"

@admin.register(CustomProfiles)
class CustomProfilesAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('phone', 'dob', is_verified, is_social)
    fieldsets = UserAdmin.fieldsets + ((None, {'fields': ('phone', 'dob')}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {'fields': ('phone', 'dob')}),)
