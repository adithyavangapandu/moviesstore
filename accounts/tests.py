from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Profile


class ProfileViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='moviefan',
            password='StrongPass123!',
        )
        self.profile = Profile.objects.create(
            user=self.user,
            city='Atlanta',
            state='GA',
            region='Southeast',
            latitude=Decimal('33.749000'),
            longitude=Decimal('-84.388000'),
        )

    def test_profile_page_shows_current_profile_details(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('accounts.profile'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'moviefan')
        self.assertContains(response, 'Atlanta')
        self.assertContains(response, 'Southeast')

    @patch('accounts.forms.ProfileLocationFormMixin._geoapify_reverse_geocode')
    def test_edit_profile_updates_username_and_location(self, mock_reverse_geocode):
        mock_reverse_geocode.return_value = {
            'results': [
                {
                    'country_code': 'us',
                    'city': 'Seattle',
                    'state_code': 'WA',
                }
            ]
        }
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('accounts.edit_profile'),
            {
                'username': 'cinephile',
                'city': 'Seattle',
                'state': 'WA',
                'lat': '47.606200',
                'lng': '-122.332100',
            },
        )

        self.assertRedirects(response, reverse('accounts.profile'))
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.user.username, 'cinephile')
        self.assertEqual(self.profile.city, 'Seattle')
        self.assertEqual(self.profile.state, 'WA')
        self.assertEqual(self.profile.region, 'Northwest')
