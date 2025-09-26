from django.contrib import admin

# Register your models here.

# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress


# Custom function to check if user's primary email is verified
# def is_verified(user):
#     try:
#         email = EmailAddress.objects.get(user=user, primary=True)
#         return email.verified
#     except EmailAddress.DoesNotExist:
#         return False
# is_verified.boolean = True  # show ✔/✖ instead of True/False
# is_verified.short_description = "Verified Email"


# # Extend the UserAdmin
# class CustomUserAdmin(UserAdmin):
#     list_display = UserAdmin.list_display + ('is_staff', 'is_superuser', is_verified)


# # Unregister the original User admin
# admin.site.unregister(User)
# # Register our custom one
# admin.site.register(User, CustomUserAdmin)
