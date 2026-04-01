from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Profile)
# signals are used whenever we want a profile created when a new user is created