from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount

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

# Custom UserAdmin
class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + (is_verified, is_social)

# Unregister default User admin
admin.site.unregister(User)
# Register custom User admin
admin.site.register(User, CustomUserAdmin)
