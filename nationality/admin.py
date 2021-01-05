from import_export import resources
from import_export.admin import ImportExportModelAdmin
from  .models import *
from django.contrib import admin

class UsaStateResource(resources.ModelResource):
    class Meta:
        model = usa_states_master
        fields = ('id', 'state_code', 'state_name')
        import_id_fields = ('id', 'state_code', 'state_name')
        #exclude = ('id', )

class UsaStateAdmin(ImportExportModelAdmin):

    resource_class = UsaStateResource
    extra = 10
    list_display = ('id', 'state_code', 'state_name')
    list_display_links = ('id', 'state_code', 'state_name')
    search_fields = ('state_code', 'state_name')
    list_per_page = 25
    #list_filter = ('id', 'state_code', 'state_name')
    ordering = ['id']

from import_export.widgets import ForeignKeyWidget
from import_export import fields
class UsaCityLatLongResource(resources.ModelResource):
    usa_state = fields.Field(
        column_name='usa_state',
        attribute='usa_state',
        widget=ForeignKeyWidget(usa_states_master, 'id'))

    class Meta:
        model = usa_cities_master
        fields = ('usa_state', 'city_name', 'county_name', 'latitude', 'longitude')
        import_id_fields = ('usa_state', 'city_name', 'county_name', 'latitude', 'longitude')
        exclude = ('id', )

class UsaCityLatLongAdmin(ImportExportModelAdmin):

    resource_class = UsaCityLatLongResource
    extra = 10
    list_display = ('id', 'usa_state', 'city_name', 'county_name', 'latitude', 'longitude')
    list_display_links = ('id', 'usa_state', 'city_name', 'county_name', 'latitude', 'longitude')
    search_fields = ('usa_state', 'city_name', 'county_name', 'latitude', 'longitude')
    list_per_page = 25
    #list_filter = ('id', 'usa_state', 'city_name', 'county_name', 'latitude', 'longitude')
    ordering = ['id']

class HashtagCollectionsResource(resources.ModelResource):
    class Meta:
        model = hashtag_collections
        fields = ('hashtag',)
        import_id_fields = ('hashtag',)
        exclude = ('id','is_locked', 'is_processed',)

class HashtagCollectionsAdmin(ImportExportModelAdmin):

    resource_class = HashtagCollectionsResource
    extra = 10
    list_display = ('id', 'hashtag', 'created_on', 'updated_on')
    list_display_links = ('id', 'hashtag', 'created_on', 'updated_on')
    search_fields = ('id', 'hashtag')
    list_per_page = 25
    #list_filter = ('id', 'hashtag', 'created_on', 'updated_on')
    ordering = ['-created_on']

# Register your models here.
admin.site.register(usa_states_master,UsaStateAdmin)
admin.site.register(usa_cities_master,UsaCityLatLongAdmin)
admin.site.register(hashtag_collections, HashtagCollectionsAdmin)
admin.site.register(data_collection_logging)

