from django.contrib import admin
from authentication.models import CustomUser
from django.contrib.auth.models import Group

admin.site.unregister(Group)
admin.site.register(CustomUser)
