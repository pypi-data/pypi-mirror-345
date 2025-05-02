from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

class CountryCodeManager(models.Manager):
    def get_by_code(self, code):
        """
        Get a country by either its 2-letter or 3-letter code.
        Args:
            code (str): A 2 or 3 letter country code
        Returns:
            CountryCode: The matching country code instance
        Raises:
            CountryCode.DoesNotExist: If no country matches the code
            ValidationError: If the code format is invalid
        """
        if not code:
            raise ValidationError("Code cannot be empty")
            
        code = code.upper().strip()
        
        if not re.match(r'^[A-Z]{2,3}$', code):
            raise ValidationError("Code must be 2 or 3 uppercase letters")
            
        try:
            if len(code) == 2:
                return self.get(iso_code=code)
            else:
                return self.get(iso_code_3=code)
        except self.model.DoesNotExist:
            raise self.model.DoesNotExist(f"No country found with code '{code}'")

class CountryCode(models.Model):
    """Model to store GENC country codes and their ISO equivalents."""
    genc_code = models.CharField(
        max_length=3,
        unique=True,
        help_text="Three-digit GENC country code"
    )
    genc_name = models.CharField(
        max_length=100,
        help_text="Official GENC name"
    )
    genc_status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="GENC status (Exception, Extension, etc.)"
    )
    iso_code = models.CharField(
        max_length=2,
        unique=False,
        null=True,
        blank=True,
        help_text="Two-digit ISO country code"
    )
    iso_code_3 = models.CharField(
        max_length=3,
        unique=False,
        null=True,
        blank=True,
        help_text="Three-digit ISO country code (if different from GENC)"
    )
    iso_code_numeric = models.CharField(
        max_length=3,
        unique=False,
        null=True,
        blank=True,
        help_text="Numeric ISO country code"
    )
    iso_name = models.CharField(
        max_length=100,
        unique=False,
        null=True,
        blank=True,
        help_text="Official ISO name"
    )
    comment = models.TextField(
        null=True,
        blank=True,
        help_text="Additional information about the country code"
    )

    objects = CountryCodeManager()

    class Meta:
        verbose_name = "Country Code"
        verbose_name_plural = "Country Codes"
        ordering = ['genc_name']

    def __str__(self):
        return f"{self.genc_name} ({self.genc_code})"

    def clean(self):
        """Validate unique constraints before saving."""
        if self.genc_code:
            qs = CountryCode.objects.filter(genc_code=self.genc_code)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({'genc_code': 'A country with this GENC code already exists.'})
                
        if self.iso_code:
            qs = CountryCode.objects.filter(iso_code=self.iso_code)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({'iso_code': 'A country with this ISO code already exists.'})
                
        if self.iso_code_3:
            qs = CountryCode.objects.filter(iso_code_3=self.iso_code_3)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({'iso_code_3': 'A country with this ISO-3 code already exists.'})
                
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class CountryField(models.CharField):
    """Custom field that can handle both 2-digit ISO, 3-digit ISO, and 3-digit GENC codes."""
    description = "A field that stores GENC country codes but accepts ISO codes (both 2 and 3 digit)"

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 3
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['max_length']
        return name, path, args, kwargs

    def to_python(self, value):
        if value is None:
            return value
        
        value = str(value).strip().upper()
        
        # If it's already a GENC code, return it
        if len(value) == 3:
            try:
                # First check if it's a GENC code
                country = CountryCode.objects.get(genc_code=value)
                return country.genc_code
            except CountryCode.DoesNotExist:
                # If not a GENC code, check if it's a 3-digit ISO code
                try:
                    country = CountryCode.objects.get(iso_code_3=value)
                    return country.genc_code
                except CountryCode.DoesNotExist:
                    pass
            
        # If it's a 2-digit ISO code, look up the GENC code
        if len(value) == 2:
            try:
                country = CountryCode.objects.get(iso_code=value)
                return country.genc_code
            except CountryCode.DoesNotExist:
                raise ValidationError(
                    _('Invalid ISO country code: %(value)s'),
                    params={'value': value},
                )
        
        raise ValidationError(
            _('Country code must be either 2 or 3 characters'),
            params={'value': value},
        )

    def get_prep_value(self, value):
        """Convert the value to a string for storage in the database."""
        if value is None:
            return value
        return str(value).upper()

    def from_db_value(self, value, expression, connection):
        """Convert the value from the database to a Python object."""
        if value is None:
            return value
        return str(value).upper()

    def value_to_string(self, obj):
        """Convert the value to a string for serialization."""
        value = self.value_from_object(obj)
        return self.get_prep_value(value) 