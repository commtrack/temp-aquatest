from django.contrib import admin
from samples.models import *

class MeasuredValueInline(admin.TabularInline):
    model = MeasuredValue
    extra = 3

class SampleAdmin(admin.ModelAdmin):
    list_display = ('taken_by','sampling_point','notes')
    search_fields = ('taken_by','sampling_point','notes')
    list_filter = ['taken_by','sampling_point']
    inlines = [MeasuredValueInline]
    fieldsets = (
        (None, {
            'fields' : ('taken_by','sampling_point','notes')
        }),
        (None, {
            'fields' : ('date_taken', 'date_received', 'modified', 'created'),
            'classes': ['wide', 'extrapretty',],
        }),
    )
admin.site.register(Sample, SampleAdmin)

class ParameterAdmin(admin.ModelAdmin):
    list_display = ('test_name','unit','lookup_hint','test_name_short')
    search_fields = ('test_name','unit','lookup_hint','test_name_short')
    list_filter = ['test_name']
admin.site.register(Parameter, ParameterAdmin)

class ValueRuleAdmin(admin.ModelAdmin):
    list_display = ('description','parameter','standard','water_use_type')
    list_filter = ['standard']
    search_fields = ('description','parameter','standard','water_use_type')
admin.site.register(ValueRule,ValueRuleAdmin)

class NormalRangeAdmin(admin.ModelAdmin):
    list_display = ('description','value_rule','minimum','maximum')
#    list_filter = []
    search_fields = ('description','value_rule')
admin.site.register(NormalRange,NormalRangeAdmin)

class AbnormalRangeAdmin(admin.ModelAdmin):
    list_display = ('description','value_rule','remedialaction','color','minimum','maximum')
#    list_filter = ['']
    search_fields = ('description','value_rule','remedialaction','color','minimum','maximum')
admin.site.register(AbnormalRange,AbnormalRangeAdmin)

