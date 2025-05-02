from django.test import TestCase
from django.db.migrations.executor import MigrationExecutor
from django.db import connection
from django_genc.models import CountryCode


class MigrationTest(TestCase):
    @property
    def app(self):
        return 'django_genc'

    def setUp(self):
        self.executor = MigrationExecutor(connection)
        self.executor.migrate([(self.app, '0001_initial')])

    def test_migration_creates_table(self):
        """Test that the migration creates the CountryCode table."""
        tables = connection.introspection.table_names()
        self.assertIn('django_genc_countrycode', tables)

    def test_migration_loads_data(self):
        """Test that the migration loads data from the CSV file."""
        # Check that at least some data was loaded
        self.assertTrue(CountryCode.objects.exists())

        # Check that a known country exists
        usa = CountryCode.objects.filter(genc_code='USA').first()
        self.assertIsNotNone(usa)
        self.assertEqual(usa.genc_name, 'UNITED STATES')
        self.assertEqual(usa.iso_code, 'US')
        self.assertEqual(usa.iso_code_3, 'USA')

    def test_migration_constraints(self):
        """Test that the migration applies all constraints."""
        # Check that GENC code is unique
        with self.assertRaises(Exception):
            CountryCode.objects.create(
                genc_code='USA',
                genc_name='Duplicate USA',
                iso_code='XX',
                iso_code_3='XXX'
            )

        # Check that ISO code is unique
        with self.assertRaises(Exception):
            CountryCode.objects.create(
                genc_code='XXX',
                genc_name='Duplicate ISO',
                iso_code='US',
                iso_code_3='XXX'
            )

        # Check that ISO-3 code is unique
        with self.assertRaises(Exception):
            CountryCode.objects.create(
                genc_code='XXX',
                genc_name='Duplicate ISO-3',
                iso_code='XX',
                iso_code_3='USA'
            ) 