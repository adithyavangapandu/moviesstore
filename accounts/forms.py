from django import forms
import requests
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from .models import Profile
class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))

regions = {
    "West": [
        "CA", "NV", "UT", "AK", "HI"
    ],
    "Northwest": [
        "WA", "OR", "ID", "MT", "WY"
    ],
    "Southwest": [
        "AZ", "NM", "TX", "OK", "CO"
    ],
    "Midwest": [
        "ND", "SD", "NE", "KS", "MN", "IA", "MO", "WI", "IL", "IN", "MI", "OH", "KY"
    ],
    "Southeast": [
        "AR", "LA", "MS", "AL", "FL", "GA", "SC", "NC", "TN"
    ],
    "Mid-Atlantic": [
        "VA", "WV", "MD", "DE", "PA", "NJ", "NY"
    ],
    "Northeast": [
        "ME", "NH", "VT", "MA", "RI", "CT"
    ]
}

def get_region(state_code):
    state = str(state_code).upper()
    for region_name, states in regions.items():
        if state in states:
            return region_name
    return ""

class ProfileMixinForm(forms.Form):
    city = forms.CharField(required=True, widget=forms.HiddenInput())
    state = forms.CharField(required=True, widget=forms.HiddenInput())
    lat = forms.DecimalField(required=True, widget=forms.HiddenInput())
    lon = forms.DecimalField(required=True, widget=forms.HiddenInput())


    def reverse_geocode(self, lat, lon):
        if not settings.GEOAPIFY_API_KEY:
            raise Exception('GEOAPIFY_API_KEY is not set in settings.py')

        url = "https://api.geoapify.com/v1/geocode/reverse?REQUEST_PARAMS"
        params = {
            'lat': lat,
            'lon': lon,
            'apiKey': settings.GEOAPIFY_API_KEY,
            'format': 'json'
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception('Error from Geoapify API: ' + response.text)
        return response.json()

    def clean(self):
        cleaned_data = super().clean()
        city = cleaned_data.get('city')
        state = cleaned_data.get('state')
        lat = cleaned_data.get('lat')
        print("Latitude cleaned:", lat)
        lon = cleaned_data.get('lon')

        data = self.reverse_geocode(lat, lon)

        results = data.get("results")
        if not results:
            raise Exception("Can't find this city")

        results_list = results[0]
        country_code = results_list.get('country_code').lower()
        if country_code != 'us':
            raise Exception("Not in the country")

        reverse_city = results_list.get("city")
        reverse_state = results_list.get("state_code")

        if not reverse_city or not reverse_state:
            raise Exception("Not valid city")

        cleaned_data['city'] = reverse_city
        cleaned_data['state'] = reverse_state

        return cleaned_data

    def save_profile(self, user):
        Profile.objects.update_or_create(
            user=user,
            defaults={
                "city": self.cleaned_data['city'],
                "state": self.cleaned_data['state'],
                "region": get_region(self.cleaned_data['state']),
                "latitude": self.cleaned_data['lat'],
                "longitude": self.cleaned_data['lon']
            }
        )[0]



class CustomUserCreationForm(ProfileMixinForm, UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update(
                {'class': 'form-control'}
            )
    def save(self, commit=True):
        user = super().save(commit=commit)
        self.save_profile(user)
        return user


class ProfileEditForm(ProfileMixinForm, forms.ModelForm):
    class Meta:
        model = User
        fields = ("username",)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['username']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update(
                {'class': 'form-control'}
            )
        user = self.instance
        profile = getattr(user, "profile", None)
        if profile is not None:
            self.fields['city'].initial = profile.city
            self.fields['state'].initial = profile.state
            self.fields['lat'].initial = profile.latitude
            self.fields['lon'].initial = profile.longitude

    def save(self, commit=True):
        user = super().save(commit=commit)
        self.save_profile(user)
        return user