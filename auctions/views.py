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
"""
@login_required
def create(request):
    form = CreateListingForm()
    return render(request, "auctions/create.html", {
        "form": form
    })