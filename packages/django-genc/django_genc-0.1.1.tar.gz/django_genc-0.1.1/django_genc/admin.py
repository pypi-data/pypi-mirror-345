from django.contrib import admin
from django_genc.models import CountryCode

@admin.register(CountryCode)
class CountryCodeAdmin(admin.ModelAdmin):
    list_display = ('genc_name', 'genc_code', 'genc_status', 'iso_code', 'iso_code_3')
    list_filter = ('genc_status',)
    search_fields = ('genc_name', 'genc_code', 'iso_code', 'iso_code_3', 'iso_name')
    ordering = ('genc_name',)
    
    fieldsets = (
        ('GENC Information', {
            'fields': ('genc_code', 'genc_name', 'genc_status')
        }),
        ('ISO Information', {
            'fields': ('iso_code', 'iso_code_3', 'iso_code_numeric', 'iso_name')
        }),
        ('Additional Information', {
            'fields': ('comment',)
        }),
    ) 