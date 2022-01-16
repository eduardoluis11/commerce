from django.contrib.auth.models import AbstractUser
from django.db import models

""" First of all, I’m getting an error saying that the table auctions_user doesn’t even exist. So, if I try to 
register a user or create a super user for the admin panel, I will get a Django error message.

That happens because, indeed, the auctions_user table doesn’t exist. I need to create a model that includes the 
parameter “user” for the table “Auctions”. Let me rewatch Brian’s video to see how to use models to create tables 
in a database to do this.

I’ll try to create at least one of the 3 models (besides the User model) to see if the ”migrations” folder gets 
created, so that the “auctions_user” table gets created. I’ll start by creating the “listings” model.

Let me see what kinds of fields I would need for listings. I would need to store the URL that has the image of the 
product, the name of the product, the initial price of the product, the name of the seller (this would be the username, 
though).

At first, I’ll forget about the admin panel, and I will work with sqlite on the CMD. That is, I will create a test 
model to generate some tables on the database, and then I’ll look at the name of the tables created using the CLI 
version of SQLite on my CMD. First, I’ll try to create a listings table by using a class on the models.py file.

First, I will create a test version of the model that I will use for the listings (source: 
https://youtu.be/YzP164YANAU?t=3059 .)

BUG FIX: Turns out that I had a bug in which makemigrations was not detecting any of the models in the models.py file. 
So, the auctions_user table and the migrations folder were never being created. 

To fix that, I needed to specify the name of the app (in this case, “auctions”, as seen on “installed apps” on the 
settings.py file) while typing the command “makemigrations”. That is, I need to execute the command 
"python manage.py makemigrations auctions" instead of "python manage.py makemigrations" (source: Dracontis’s reply from 
https://stackoverflow.com/questions/32518804/django-makemigrations-not-detecting-new-model  .) 
Also, since my database had bugs, I needed to delete the database, and then run “makemigrations” to recreate it. 
Otherwise, I would get an error message while executing the “migrate” command to apply the changes to the database.
"""
class Listings(models.Model):
    description = models.CharField(max_length=255)


class User(AbstractUser):
    pass


