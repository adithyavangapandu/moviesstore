from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile


class LocalPopularityMapFilterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='viewer', password='testpass123')
        self.client.login(username='viewer', password='testpass123')
        self._create_profile(
            self.user,
            city='Atlanta',
            state='GA',
            region='Southeast',
            latitude='33.749000',
            longitude='-84.388000',
        )
        self._create_profile(
            User.objects.create_user(username='augusta', password='testpass123'),
            city='Augusta',
            state='GA',
            region='Southeast',
            latitude='33.473500',
            longitude='-82.010500',
        )
        self._create_profile(
            User.objects.create_user(username='birmingham', password='testpass123'),
            city='Birmingham',
            state='AL',
            region='Southeast',
            latitude='33.518600',
            longitude='-86.810400',
        )
        self._create_profile(
            User.objects.create_user(username='phoenix', password='testpass123'),
            city='Phoenix',
            state='AZ',
            region='Southwest',
            latitude='33.448400',
            longitude='-112.074000',
        )
        self._create_profile(
            User.objects.create_user(username='tucson', password='testpass123'),
            city='Tucson',
            state='AZ',
            region='Southwest',
            latitude='32.222600',
            longitude='-110.974700',
        )
        self._create_profile(
            User.objects.create_user(username='dallas', password='testpass123'),
            city='Dallas',
            state='TX',
            region='Southwest',
            latitude='32.776700',
            longitude='-96.797000',
        )

    def _create_profile(self, user, **profile_data):
        return Profile.objects.create(user=user, **profile_data)

    def test_region_filter_limits_state_options_and_populates_region_city_options(self):
        response = self.client.get(
            reverse('movies.local_popularity_map'),
            {'region': 'Southwest'},
        )

        template_data = response.context['template_data']

        self.assertEqual(template_data['selected_region'], 'Southwest')
        self.assertEqual(
            template_data['states'], [
                {'value': 'AZ', 'label': 'AZ'},
                {'value': 'TX', 'label': 'TX'},
            ]
        )
        self.assertEqual(
            template_data['city_filter_options'],
            [
                {'value': 'Dallas|TX', 'label': 'Dallas, TX'},
                {'value': 'Phoenix|AZ', 'label': 'Phoenix, AZ'},
                {'value': 'Tucson|AZ', 'label': 'Tucson, AZ'},
            ],
        )

    def test_state_filter_autopopulates_region_and_limits_city_options(self):
        response = self.client.get(
            reverse('movies.local_popularity_map'),
            {'state': 'ga'},
        )

        template_data = response.context['template_data']

        self.assertEqual(template_data['selected_region'], 'Southeast')
        self.assertEqual(template_data['selected_state'], 'GA')
        self.assertEqual(
            template_data['city_filter_options'],
            [
                {'value': 'Atlanta|GA', 'label': 'Atlanta, GA'},
                {'value': 'Augusta|GA', 'label': 'Augusta, GA'},
            ],
        )

    def test_city_filter_autopopulates_parent_filters(self):
        response = self.client.get(
            reverse('movies.local_popularity_map'),
            {'city': 'Phoenix|AZ'},
        )

        template_data = response.context['template_data']

        self.assertEqual(template_data['selected_region'], 'Southwest')
        self.assertEqual(template_data['selected_state'], 'AZ')
        self.assertEqual(template_data['selected_city_value'], 'Phoenix|AZ')
        self.assertEqual(template_data['active_scope'], 'Phoenix, AZ')

    def test_more_specific_filter_overrides_conflicting_parent_filter(self):
        response = self.client.get(
            reverse('movies.local_popularity_map'),
            {'region': 'Southeast', 'state': 'AZ'},
        )

        template_data = response.context['template_data']

        self.assertEqual(template_data['selected_region'], 'Southwest')
        self.assertEqual(template_data['selected_state'], 'AZ')

    def test_city_options_empty_without_region_or_state(self):
        response = self.client.get(reverse('movies.local_popularity_map'))

        template_data = response.context['template_data']

        self.assertEqual(template_data['selected_region'], '')
        self.assertEqual(template_data['selected_state'], '')
        self.assertEqual(template_data['city_filter_options'], [])
