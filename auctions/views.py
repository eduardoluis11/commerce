from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

""" This will let me use the "@login_required" attribute (source: 
https://docs.djangoproject.com/en/4.0/topics/auth/default/#the-login-required-decorator )
"""
from django.contrib.auth.decorators import login_required

"""  This will let me use the Django form for creating listings, which is on the forms.py file (source: 
https://docs.djangoproject.com/en/4.0/topics/forms/ )
"""
from .forms import CreateListingForm

from .models import User

# This will import the Listings table from the models.py file
from .models import Listings

def index(request):
    return render(request, "auctions/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


""" 2.a) Users should be able to visit a page to create a new listing.

For this, I’ll just create a route. I’ll make a view in views.py, add the URL in urls.py, and add the link into the 
layout.html or index.html (although I think it would be best to put it on layout.html, since I want users to be able 
to access the page to create a new listing from anywhere within the website.) I’ll open the website to see if the 
distribution code already added a text that says “create new page” so that I can insert a link there.

No, there isn’t any text saying “Create New Listing” if the user logs in into their account. I need to add the text, 
and add the link. And, as I said, I prefer adding the “Create new listing” link in layouts.html so that the user can 
create a new listing in any page within the website. I will put it somewhere close to the “log out” link. Upon further 
inspection, I see that there is a “nav” class within layouts.html, which serves as a navbar. I will insert within 
that <ul> tag with class “nav” the text with the “Create new listing” link.

I need to use the @login_required decorator on the line right before creating the view function for creating new 
listings in views.py so that only users that have logged in into their accounts can create listings. That is, I need 
to put the line “@login_required” right on top of “def function_name():” in views.py.

I will at first create a simple view function in views.py, which will only redirect the user to the create.html page. 
I will call the function “create(request)”. I won’t check for POST requests yet. To redirect them to the create.html 
page, I will use the following snippet: return render(request, "auctions/create.html") .

Next, I would need to edit the urls.py file to add the path towards the “/create” URL.

Then, in the views.py file, to render the form (if the user has just entered the page), I will have to first import 
that form. That’s done using “from .forms import NameOfTheForm”. Then, within the view() function, I need to add a 
variable, and make that variable equal to “NameOfTheForm()” (source: 
https://docs.djangoproject.com/en/4.0/topics/forms/ .) Finally, I will send that form to create.html using jinja 
notation. To do that, I will have to put that variable inside the “return render request()” function, by using the 
following syntax: {“form_variable”: form_variable}. Then, I need to call that variable via Jinja notation in 
create.html.

I will add some debugging code to print the data stored in the Listings table from the database into the /create 
page. I will do that just to learn how to print data from the database into the website. To do that, in the create() 
view, I will add Django’s Query Set notation into a variable. Then, I will send that variable to the /create page via 
Jinja notation. The syntax that I should use will be something like: “ “variable_name”: Model_name.objects.all() .”

I will now proceed to insert the data from the form’s inputs from the create page into the database. To do that, I 
will obtain the data from the POST request from the /create page, and I will insert it into an “if” statement. I will 
insert all of that data into multiple variables. Then, I will insert those variables into the different fields of the 
Listings table in the database. But, to do that, I need to obtain the ID number from the user that’s currently logged 
in, so that the listing is created for that specific user.

The data from the user that’s currently logged in is stored into the request of the different views functions, and I 
can access it by using the following snippet: “request.user” (source: K Z’s answer from 
https://stackoverflow.com/questions/12615154/how-to-get-the-currently-logged-in-users-user-id-in-django . So, if I 
use something like “logged_user = request.user” to store all of the data from the logged in user, I can access their 
PK by using the following snippet: “logged_user_id = logged_user.id”.)

To get data from an input via a POST request from a form in a view() with an “if” statement, I need to use the 
following syntax in the view(): to check if a POST request was made: " if request.method == "POST":  " (source: 
Brian’s lecture for this assignment). Then, to insert the data from the form into a variable in the view(), I need to 
use the following syntax: " request.POST["input_name"]  ", and I need to insert that into a variable.  

Now, to insert the data from that form into my database, I will need to use Django’s Query Set syntax. The syntax that 
I will need to use will be: " table.field.add(variable_with_input_data) ".That will add a row, that is, an entry, 
into that table in my database. The problem is that I don’t want to add just one field into that row. I want to add 
like 7 or 8 fields within that same row, that is, within that same listing. So, I think I will have to use the “ 
variable.save() ” syntax that Brian used when he was explaining how to use the Query Set syntax on the Python shell.

The Query Set syntax that I will use to insert the 3 fields of the form, as well as all of the other remaining 4 or 5 
fields into a single listing in the Listings table in the database, I will use syntax like the following: 
new_listing = Listings(seller_id=logged_user_id, product_name=product_name_variable_from_input, 
description=description_variable, initial_price=price_variable, …, active=True). Then, to save that into the database, 
I’ll need to use the following syntax: “ new_listing.save() ”.

To insert the PK of a user, I need to get an instance of the User table, or I’ll get an error when trying to execute 
the Query Set syntax. To get an instance of the User table, I need to use the following syntax: “ 
user = User.objects.get(id=id_number_from_user) “ (source: JamesO’s answer from 
https://stackoverflow.com/questions/9616569/django-cannot-assign-u1-staffprofile-user-must-be-a-user-instance .)
"""
@login_required
def create(request):
    form = CreateListingForm()  # Form from forms.py to create a new listing

    logged_user = request.user      # This stored the data from the currently logged in user
    logged_user_id = logged_user.id     # PK of the currently logged in user

    # This creates an instance of the User table, which I'll need to use in the Query Set syntax
    user_instance = User.objects.get(id=logged_user_id)


    if request.method == "POST":
        listing_title = request.POST["listing_title"]
        starting_bid = request.POST["starting_bid"]
        description = request.POST["description"]

        # This prepares the new listing data before inserting it into the database
        new_listing = Listings(seller_id=user_instance, product_name=listing_title,
                               description=description, initial_price=starting_bid, active = True)

        # This inserts the new listing into the database
        new_listing.save()

        return render(request, "auctions/create.html", {
            "form": form,
            "listings": Listings.objects.all()
        })

    else:
        return render(request, "auctions/create.html", {
            "form": form,
            "listings": Listings.objects.all()
        })