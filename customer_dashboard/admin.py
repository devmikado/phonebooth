from django.contrib import admin
from .models import connectedSocialAccount


class ConnectedSocialAccountAdmin(admin.ModelAdmin):
    list_display = ('social_account', 'user', 'account')


admin.site.register(connectedSocialAccount, ConnectedSocialAccountAdmin)
