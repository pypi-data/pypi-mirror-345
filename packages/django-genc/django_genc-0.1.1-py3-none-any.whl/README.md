# django-genc

A reusable Django app for working with GENC (Geopolitical Entities, Names, and Codes) country codes. Source data comes from the [NGA site](https://nsgreg.nga.mil/registries/browse/results.jsp?registryType=genc&registerField=IE4&itemTypeField=ggp&gce=all&field=name&show=all&status=all&sort=nameasc) and the [CIA World Fact Book](https://www.cia.gov/the-world-factbook/references/country-data-codes/).

## Features

- Store and manage GENC country codes with their ISO equivalents
- Custom `CountryField` that accepts both 2-character and 3-character ISO and 3-character GENC codes
- Admin interface integration

## Installation

1. Install the package:

```bash
pip install django-genc
```

2. Add 'django_genc' to your INSTALLED_APPS:

```python
INSTALLED_APPS = [
    ...
    'django_genc.apps.GencConfig',
    ...
]
```

3. Run migrations:

```bash
python manage.py migrate
```

## Usage

### Models

```python
from django.db import models
from django_genc.models import CountryField

class MyModel(models.Model):
    country = CountryField()
```

## API

### CountryField

A custom field that can handle both 2-digit ISO and 3-digit GENC codes.

```python
from django_genc.models import CountryField

class MyModel(models.Model):
    country = CountryField()
```

The field will:
- Store values as 3-digit GENC codes in the database
- Accept both 2-digit ISO and 3-digit GENC codes as input
- Automatically convert ISO codes to GENC codes
- Validate that the code exists in the database

### CountryCode Model

The base model for storing country codes:

```python
from django_genc.models import CountryCode

# Get a country by GENC code
country = CountryCode.objects.get(genc_code='USA')

# Get a country by ISO code
country = CountryCode.objects.get(iso_code='US')

# Look up a country by a code under either standard
country = CountryCode.objects.get_by_code('US')
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details. 