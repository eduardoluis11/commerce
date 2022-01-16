from django.contrib import admin

""" According to Django's documentation, if I'm going to use "AbstractUser" as a model in models.py, I 
should import it here, in the admin.py file (source: https://docs.djangoproject.com/en/4.0/topics/auth/customizing/)
"""
from .models import User

# Register your models here.
