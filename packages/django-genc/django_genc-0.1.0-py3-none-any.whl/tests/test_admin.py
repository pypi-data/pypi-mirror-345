from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django_genc.models import CountryCode


class CountryCodeAdminTest(TestCase):
    def setUp(self):
        # Create a superuser
        self.user = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password'
        )
        self.client = Client()
        self.client.login(username='admin', password='password')

        # Create a test country
        self.country = CountryCode.objects.get(
            genc_code='USA'
        )

    def test_admin_list_view(self):
        """Test that the admin list view works and shows all fields."""
        url = reverse('admin:django_genc_countrycode_changelist')
        response = self.client.get(url, {'q': 'USA'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'USA')
        self.assertContains(response, 'UNITED STATES')
        self.assertContains(response, 'Exception')
        self.assertContains(response, 'US')

    def test_admin_detail_view(self):
        """Test that the admin detail view works and shows all fields."""
        url = reverse('admin:django_genc_countrycode_change', args=[self.country.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'USA')
        self.assertContains(response, 'UNITED STATES')
        self.assertContains(response, 'Exception')
        self.assertContains(response, 'US')

    def test_admin_search(self):
        """Test that the admin search functionality works."""
        url = reverse('admin:django_genc_countrycode_changelist')
        
        # Search by GENC code
        response = self.client.get(url, {'q': 'USA'})
        self.assertContains(response, 'UNITED STATES')
        
        # Search by GENC name
        response = self.client.get(url, {'q': 'UNITED STATES'})
        self.assertContains(response, 'UNITED STATES')
        
        # Search by ISO code
        response = self.client.get(url, {'q': 'US'})
        self.assertContains(response, 'UNITED STATES')

    def test_admin_filter(self):
        """Test that the admin filters work."""
        url = reverse('admin:django_genc_countrycode_changelist')
        
        # Filter by GENC status
        response = self.client.get(url, {'genc_status': 'Exception', 'q': 'USA'})
        self.assertContains(response, 'UNITED STATES')
        
        # Filter by non-existent status
        response = self.client.get(url, {'genc_status': 'NonExistent'})
        self.assertNotContains(response, 'UNITED STATES') 