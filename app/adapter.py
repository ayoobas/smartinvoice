from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .models import Invoice

class ObazSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, data):
        # 1. Save the default User object first

        user = super().populate_user(request, sociallogin, data)
        user.email = data.get('email')
        return user
        
    def save_user(self, request, sociallogin, form=None):
        # 1. Save the User (now with the email from populate_user)
        user = super().save_user(request, sociallogin, form)
        
        # 2. Extract Google data for your custom model
        data = sociallogin.account.extra_data
        full_name = data.get('name', user.username)
        email = data.get('email')

        # 3. Update or Create CustomerInfo
        Invoice.objects.update_or_create(
            email=email,
            defaults={
                'name': full_name,
                'address': "Logged in via Google" 
            }
        )
        return user