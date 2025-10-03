from allauth.socialaccount.models import SocialAccount
from django.shortcuts import render
def is_social(user):
    """
    Returns True if the user has at least one SocialAccount (logged in via Google/GitHub)
    """
    return SocialAccount.objects.filter(user=user).exists()

is_social.boolean = True
is_social.short_description = "Third-Party Login"


def home(request):
    return render(request,'index.html')