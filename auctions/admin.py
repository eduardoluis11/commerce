from django.contrib import admin

""" According to Django's documentation, if I'm going to use "AbstractUser" as a model in models.py, I 
should import it here, in the admin.py file (source: https://docs.djangoproject.com/en/4.0/topics/auth/customizing/)
"""
from .models import User

""" I need to import my models into admin.py in order to be able to activate the admin panel (according to Brian’s 
lecture).
"""

# This imports the models
from .models import Listings, Comments, Bids, Watchlists, Categories

# Register your models here.
admin.site.register(Listings)
admin.site.register(Comments)
admin.site.register(Bids)
admin.site.register(Watchlists)
admin.site.register(Categories)




