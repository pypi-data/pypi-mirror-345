from django.test import TestCase
from django.core.exceptions import ValidationError
from django_genc.models import CountryCode


class CountryCodeModelTest(TestCase):
    def setUp(self):
        # Clear existing data
        CountryCode.objects.all().delete()
        
        # Create a test country code
        self.country = CountryCode.objects.create(
            genc_code='TST',
            genc_name='Test Country 1',
            genc_status='Standard',
            iso_code='T1',
            iso_code_3='TST',
            iso_code_numeric='001',
            iso_name='Test Country One',
            comment='Test country'
        )

    def test_country_code_creation(self):
        """Test that a country code can be created with all fields."""
        self.assertEqual(self.country.genc_code, 'TST')
        self.assertEqual(self.country.genc_name, 'Test Country 1')
        self.assertEqual(self.country.genc_status, 'Standard')
        self.assertEqual(self.country.iso_code, 'T1')
        self.assertEqual(self.country.iso_code_3, 'TST')
        self.assertEqual(self.country.iso_code_numeric, '001')
        self.assertEqual(self.country.iso_name, 'Test Country One')
        self.assertEqual(self.country.comment, 'Test country')

    def test_unique_constraints(self):
        """Test that unique constraints are enforced."""
        # Try to create another country with the same GENC code
        with self.assertRaises(ValidationError):
            CountryCode.objects.create(
                genc_code='TST',
                genc_name='Another Test Country',
                iso_code='XX',
                iso_code_3='XXX'
            )

        # Try to create another country with the same ISO code
        with self.assertRaises(ValidationError):
            CountryCode.objects.create(
                genc_code='TS2',
                genc_name='Another Country',
                iso_code='T1',
                iso_code_3='XXX'
            )

        # Try to create another country with the same ISO-3 code
        with self.assertRaises(ValidationError):
            CountryCode.objects.create(
                genc_code='TS2',
                genc_name='Another Country',
                iso_code='XX',
                iso_code_3='TST'
            )

    def test_optional_fields(self):
        """Test that optional fields can be null."""
        country = CountryCode.objects.create(
            genc_code='TS2',
            genc_name='Test Country 2',
            genc_status=None,
            iso_code=None,
            iso_code_3=None,
            iso_code_numeric=None,
            iso_name=None,
            comment=None
        )
        self.assertIsNone(country.genc_status)
        self.assertIsNone(country.iso_code)
        self.assertIsNone(country.iso_code_3)
        self.assertIsNone(country.iso_code_numeric)
        self.assertIsNone(country.iso_name)
        self.assertIsNone(country.comment)

    def test_string_representation(self):
        """Test the string representation of the model."""
        self.assertEqual(str(self.country), 'Test Country 1 (TST)')

    def test_ordering(self):
        """Test that countries are ordered by GENC name."""
        CountryCode.objects.create(
            genc_code='TS2',
            genc_name='Test Country 2',
            iso_code='T2',
            iso_code_3='TS2'
        )
        CountryCode.objects.create(
            genc_code='TS3',
            genc_name='Test Country 3',
            iso_code='T3',
            iso_code_3='TS3'
        )

        countries = list(CountryCode.objects.all())
        self.assertEqual(countries[0].genc_name, 'Test Country 1')
        self.assertEqual(countries[1].genc_name, 'Test Country 2')
        self.assertEqual(countries[2].genc_name, 'Test Country 3') 