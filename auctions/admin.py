from django.contrib import admin

""" According to Django's documentation, if I'm going to use "AbstractUser" as a model in models.py, I 
should import it here, in the admin.py file (source: https://docs.djangoproject.com/en/4.0/topics/auth/customizing/)
"""
from .models import User

""" I need to import my models into admin.py in order to be able to activate the admin panel (according to Brian’s 
lecture).

Then, I need to register my models. Although the assignment says that I should only add “listings, comments, and bids” 
to the admin panel, I will also add “categories”. That is because, normally, if I want to add a category, I need to 
manually go to the CMD, and add SQL commands to insert more categories into the web app. It would be way easier if I 
could do it from the admin panel. 

As for the watchlists, I really don’t know whether to leave it, or remove it. I might remove it.

"""

# This imports the models
from .models import Listings, Comments, Bids, Watchlists, Categories

# Register your models here.
admin.site.register(Listings)
admin.site.register(Comments)
admin.site.register(Bids)
# admin.site.register(Watchlists)
admin.site.register(Categories)




