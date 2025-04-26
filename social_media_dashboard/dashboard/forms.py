from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['twitter_handle', 'facebook_token', 'bio', 'profile_pic']