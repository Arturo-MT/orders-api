from django.contrib import admin
from authentication.models import CustomUser, AccountSettings
from django.contrib.auth.models import Group

admin.site.unregister(Group)
admin.site.register(CustomUser)
admin.site.register(AccountSettings)
