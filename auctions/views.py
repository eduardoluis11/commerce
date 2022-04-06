from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

""" This will let me obtain the current date and time whenever I create a listing (source: 
https://pythonguides.com/how-to-get-current-time-in-django/ )
"""
import datetime

""" This will let me use the "@login_required" attribute (source: 
https://docs.djangoproject.com/en/4.0/topics/auth/default/#the-login-required-decorator )
"""
from django.contrib.auth.decorators import login_required

"""  This will let me use the Django form for creating listings, which is on the forms.py file (source: 
https://docs.djangoproject.com/en/4.0/topics/forms/ )
"""
from .forms import CreateListingForm

from .models import User

# This will import the Listings,Categories, and all the other tables from the models.py file
from .models import Listings, Categories, Bids, Comments, Watchlists

""" 
I can show the active listings in the home page, regardless of whether the user has logged in or not. Remember 
that you don’t have to be logged in in eBay in order to see a product and their price. You only need to log in to buy 
or sell a product.

I need to send all of the resulting data into index.html, NOT to create.html. I want to display the listings on 
the home page, NOT on the page for creating a new listing. So, I’ll need to specify that on the views.py file.

"""
def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listings.objects.all()
    })


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

I need to fix the formatting of the database entries from the Categories model. I will use the 
"strip()" function (source: https://www.codegrepper.com/code-examples/python/remove+outer+quotes+from+string+python ) 

BUG FIX: This fixes the issue of the category name being displayed being its ID number instead of the category.
What I do is first, obtain the ID of the category from the Create Listing form. Then, I create a variable which will
obtain the name of the category whose ID number is the one obtained from the Create Listing form. Finally, I 
use that variable to display that entry of the database. Now, both the dropdown menu and the databse entry show
the proper format for the categories for the listings (source: iridescent's reply from 
https://stackoverflow.com/questions/4300365/django-database-query-how-to-get-object-by-id .)

BUG: If the user doesn’t choose a category, the category will be ‘’ (NULL), so I’ll get an error message from Django. 
That is because I’m trying to find an entry with the ID number that is NULL or ‘’, which, of course, doesn’t exist. If 
I fix this bug (with an “if” statement), I will finish this part of the homework.

I’ll put an “if” statement saying that, if the user types “ ‘’ ” as the category, that it should insert “category” in 
the “category_formatted” variable. Otherwise, I will use the query set statement that will look for the category name 
whose ID is the one inserted in the form submitted by the user.

BUG: For some reason, the only date being displayed is Jan 1st, 2022. 

The database is displaying the date of creation for all of the listings to be jan 1st, 2022. I need to see what went 
wrong. It may be that it’s inserting the default ate that I specified, instead of taking the current date and time of 
creation of the entry. After checking aout my code on models.py, I can confirm that the default date that I specified 
is indeed January 1st, 2022. I need to modofy the code to take the current date and time whenever I create a new 
listing.

In my views.py file, I’m never obtaining the date from anywhere, neither from the form, nor from a Query Set 
statement. So, I will have to use the proper Query Set statement to grab the current date and time, and insert in into 
the “created_on” variable, that is, inside of each listings’ entry.

It seems that I need to import a Python library called “datetime”, and then I need to use this snippet on the views.py 
file: “datetime.now()” (source: https://pythonguides.com/how-to-get-current-time-in-django/ .)

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
        picture_url = request.POST["picture_url"]
        category = request.POST["category"]

        # This obtains the current date and time
        current_date_and_time = datetime.datetime.now()


        # This removes the parentheses from the Categories entries.
        # category_formatted = category.strip('(')

        # This checks if the user selected a category
        if category != '':
            # This gets a category name by its PK, which is obtained from the form
            category_formatted = Categories.objects.get(pk=category)

        # If the user didn't select a category, no category will be inserted
        else:
            category_formatted = category

        # This prepares the new listing data before inserting it into the database
        new_listing = Listings(seller_id=user_instance, product_name=listing_title,
                               description=description, initial_price=starting_bid, picture_url=picture_url, 
                               category=category_formatted, created_on=current_date_and_time, active = True)

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

""" This will display a page for a specific listing if the user clicks on a listing on the home page.

Now, I need to go to urls.py, since I need to create a page specific for each listing. I will use the ID of each 
listing to differentiate the URL from each listing page. To do that, I will need to insert the ID of the currently 
clicked listing into a string from the views.py field (if I’m not mistaken), and then insert it into the “<str” 
keyword in urls.py.

To get the seller’s name on the views.py file, first, I will get the seller’s ID from the listing’s entry. The specific 
field that I want from the Listings table is called “seller_id_id”, which I’ll need to store in a variable. Then, I need 
to call the User table, and find a user whose ID is the same as the one in the listing for that particular page. Finally, 
I want to obtain the username of that user, and then send it to listing.html.

What I ended up doing was to obtain the ID of the current listing, and all of the IDs of all of the users. Then, in jinja 
notation on the listing.html file, I used an “if” statement comparing the seller’s ID from the current listing, and all 
the IDs from all of the users. If they are the same, the name of the seller will be printed. 

I already have created the model for the watchlists. So, I will use a Query Set statement to add a currently selected product 
into the Watchlist table as an entry. The first thing that I’ll need will be the ID code of the product. I don’t know if 
I’m storing it as a foreign key, but, ideally, it should be that way. After checking, it turns out that I didn’t use a foreign 
key, but a “OneToMany” and “ManyToMany” functions for the user ID and the listing ID for the Watchlist table. The columns for 
the Watchlist table are User and the Listings tables (which probably takes the ID code for those tables), and the listing’s URL.
	
So, the Query Set statement that I’ll use to insert the product into a watchlist will insert that product’s URL, ID, and seller 
ID into the Watchlist table in the database. The columns are “listing_url”, “user”, and “listing”. “listing_url” refers to the 
URL for the selected product. “user” refers to the currently logged in user. Finally, “listing” refers to the currently 
selected product.

I’ll add a button that says “Add to Watchlist” once the user clicks on a product and enters that product’s page. If the user 
has already added that product to their watchlist, the button will change to “Remove from watchlist”, which will remove the 
item from the user’s watchlist.

The table I’m interested in is called “auctions_watchlists”. There’s a similar table called “auctions_watchlists_user”. I think 
this last table was automatically created since I’m using a “many to many” relationship function for the “user” column (the 
column that gets the seller’s ID). 

So, I will first create a button in the listing pages that say something like “Add to Watchlist”. Then, I will add in views.py 
a Query Set on the view for the individual listing pages that will insert the seller ‘s ID, the listing ID, and the listing’s 
URL into the “auctions_watchlists” table. The button can be styled using Bootstrap. I could put the button below the price. 
After further consideration, I decided to put it under the description.

To insert the logged in user’s data in the “user” column for the Watchlist table, I will obtain the logged in user’s ID from the 
“request.user” function. Then, I’ll get that user by usign a Query Set statement looking for a user with the ID belonging to 
the currently logged in user.

Then, to insert the currently selected product’s data into the “listing” column of the Watchlist table, I will use a Query Set 
statement to get the product whose ID is the one that’s typed on the URL bar. That’s already being inserted in the 2nd 
parameter of the display_listing() view (which is called “listing_id”).

Now, getting the URL of the currently selected product will be a bit tricky. I need to select the entire text that’s 
inserted in the URL bar. I will use the URL used in the urls.py file for the display_listing() view as a template. So, I 
may insert the URL “listing/listing_id>” in the “listing_url” column.

Note: DO NOT USE get() on Listings.objects, since I would get an error that won't let me enter the page for a specific
product. I should keep the filter() function. 

BUG: I'm getting an error telling me that I have issues when trying to assign the value to a Many To Many field, which,
in my case, is the "product_id" field fro the Watchlist table. To fix that, it seems that I need to save the Query Set 
statement without the user, and THEN I need to add the user using something like "user.add(request.user)" (source:
https://geeksqa.com/django-direct-assignment-to-the-forward-side-of-a-many-to-many-set-is-prohibited-use-user-set-instead
)

BUG: The product page's URL is not being properly inserted into the database. What I'll do is to store the URL into 2
parts: one with the word "listing/", and the other half with the product's ID. Then, I will concatenate both variables
in a single variable using the "+" sign (source: https://www.educative.io/edpresso/how-to-concatenate-strings-in-python
.)

The ID of the products are NOT stored on the auctions_watchlists table: instead, they’re being inserted in a new table 
that was automatically created called “auctions_watchlists_product_id”. This happened because the product_id column is 
stored as a One To Many field, which generates a table. The auctions_watchlists_product_id stores the ID of each entry 
on the watchlist, the ID of each entry in this new table, and the ID of the product added to the watchlist.

Each watchlist doesn’t have their own ID. To separate one watchlist from the other, I have to use the ID of the user 
who’s the owner of that watchlist. That way, I’ll use a filter to find all of the products added by a person by using 
that person’s ID on the auctions_watchlist table.

Now that the product is being properly added into the watchlist after clicking on the “Add to Watchlist” button, I need 
to change that button into “Remove from Watchlist” after the user adds that product into their wish list. Then, after 
clicking the “Remove” button, that product will be removed from the Watchlist table in the database.

The ID of the products are NOT stored on the auctions_watchlists table: instead, they’re being inserted in a new table 
that was automatically created called “auctions_watchlists_product_id”. This happened because the product_id column is 
stored as a Many To Many field, which generates a table. The auctions_watchlists_product_id stores the ID of each entry 
on the watchlist, the ID of each entry in this new table, and the ID of the product added to the watchlist.

Each watchlist doesn’t have their own ID. To separate one watchlist from the other, I have to use the ID of the user 
who’s the owner of that watchlist. That way, I’ll use a filter to find all of the products added by a person by using 
that person’s ID on the auctions_watchlist table.

So, to change the “Add to Watchlist” button to “Remove from Watchlist”, and the removing that product from that user’s 
watchlist, I’ll have to make an “if” statement using Django on the display_listing.html page. I’ll specify that, if 
that particular user doesn’t have that product on his list, to display “Add to Watchlist”. Otherwise, it should display 
a button that says “Remove from Watchlist”.

I need to get all of the IDs for the entries of the auction_watchlist table for the logged in user. Then, I need to 
compare those IDs with the watchlist IDs stored in the auctions_watchlists_product_id. Since there will be inevitable 
a match (since one of those tables has a Many To Many relationship with the other), I will compare those results with 
the ID of the listing I’m currently in (which is stored in the listing_id variable in the display_entry() view.) If 
the product where I’m currently in has the same ID as one of the products in the user’s watchlist, I should show the 
“Remove” button. Otherwise, I should show the “Add to watchlist” button.

Actually, the “if” statement to decide whether to show the “Add to Watchlist” or “Remove” button is less complicated 
than I’m making it to be. I only need to check the number for the product ID on the product page’s URL (which is 
stored in the listing_id parameter on the display_listing() view), and compare it with all of the products stored on 
that user’s watchlist. If there’s a match, I will display the “Remove” button. Otherwise, I will display the “Add 
to Watchlist” button.

Then, I will send the listing_id parameter and the results of the subquery to the display_listing.html file from the 
display_listing() function. Then, using Jinja, I will use an “if” statement that checks if the number in the listing
is inside of the subquery. If it is, I will display the “Remove” button. Otherwise, I will display the “Add to 
Watchlist” button.

To check if the user has a product on their watchlist, I will make a subquery which will take data from both the 
auctions_watchlists and the auctions_watchlists_product_id tables. In this case, I only want the product IDs for the 
watchlist for the currently logged in user. I will do the subquery using Query Set notation, not SQL. To do that, I 
will first make a Query Set query to obtain all of the IDs from the Watchlist table for the currently logged in user. 
Then, I would make a query on the auctions_watchlists_product_id table to look for all of the products, but only 
those whose watchlist ID match those as the ones in the previous query (source: Ramast’s reply from 
https://stackoverflow.com/questions/8556297/how-to-subquery-in-queryset-in-django .)

Upon further consideration, I don’t even need to use a subquery to check if the user added a product to their 
watchlist. I could simply use a Query set query to select all items on the Watchlist table for the currently logged in 
user, and send it to the listing.html file. Then, with an “if” statement, I would check if the ID of the current number 
is inside that “array” with the user’s products. If it is, I will display the “remove” button.

I could check if the number stored in the parameter "listing_id" exists in the Watchlist table for the currently
logged-in user using an "if" statement through notation like the following: "if listing_id in Watchlists.objects.filter"
(source: Siddharth Gupta's reply from 
https://stackoverflow.com/questions/32002207/how-to-check-if-an-element-is-present-in-a-django-queryset .)

By looking at my submission for the “Wiki” homework assignment, I think I may have the solution that I’m looking for to check 
when to display the “Remove” or the “Add to Watchlist” buttons. I will first go to the views.py file to the view that displays 
that page for a particular listing/product. Here, I will declare an empty array, which will be used for storing all of the 
products in the watchlist from the currently-logged user. Then, I will create a “for” loop and an “if” statement to populate 
that array with all of the products stored ina a watchlist that belong to the currently-logged user. Then, I will send that 
array to the listing.html page. 

Then, I will go to the listing.html file, and I will use Jinja notation. Here, I will use a “for” loop and an “if” statement 
to check for each product within the array with the products stored in the user’s watchlist. If that array has a product with 
the same ID as the current product being displayed on the webpage, that means the user has that product already stored on 
their watchlist. So, I will display the “Remove” button. Otherwise, I will display the “Add to Watchlist” button.

To store the product IDs, I need to use the "values_list()" from the Query Set notation (source: 
https://docs.djangoproject.com/en/4.0/ref/models/querysets/ .)

To remove the parentheses and the quotations marks when using values_list() while using a Query Set statement, 
I need to add the parameter "flat=True" (source: https://docs.djangoproject.com/en/4.0/ref/models/querysets/ .)

I was finally able to modify the button from "Add to Wishlist" to "Remove". To do it, I needed to convert both
the listing_id variable (the parameter that stores the ID for the product whose page the user has currently clicked
on) and the "product" (or "i") variable in the "for" loop that populates the user's watchlist into integers. That
way, I can safely compare both numbers. If both numbers are the same, a boolean variable will tell the "Remove"
button to appear on the product's page. Otherwise, the "Add to Watchlist" will appear. To convert a value into an
integer, I need to use the int() function (source: 
https://www.freecodecamp.org/news/python-convert-string-to-int-how-to-cast-a-string-in-python/#:~:text=To%20convert%2C%20or%20cast%2C%20a,int(%22str%22)%20.)

BUG: The "Add to Watchlist" button doesn't change to "Remove" immediately after adding a product to that user's watchlist.
Instead, I have to exit the currently selected product's page, and the re-enter it so that I can notice the difference.
So, I will try reloading the current page by using HttpResponseRedirect.

"""
def display_listing(request, listing_id):
    # This obtains the listing that I want to display as iterable objects
    current_listing = Listings.objects.filter(id=listing_id)

    # This obtains a specific instance of a listing, which I'll need to store the listing in a watchlist
    current_listing_instance = Listings.objects.get(id=listing_id)

    # This stores the seller ID of the current listing
    # seller_id = current_listing.seller_id

    # This obtains all of the data from all of the sellers
    seller = User.objects.all()

    logged_user = request.user      # This stored the data from the currently logged in user
    logged_user_id = logged_user.id     # PK of the currently logged in user

    # This creates an instance of the User table, which I'll need to use in the Query Set syntax
    user_instance = User.objects.get(id=logged_user_id)

    # This array will store all of the products from a user's watchlist
    watchlist_array = []

    # This will make it so that the "Remove" button won't appear by default, and to prevent a bug that makes 
    # the "Add to Watchlist" button to appear multiple times
    display_remove_button = False

    # This gets all the products inside the currently logged-in user's watchlist
    users_products_in_watchlist = Watchlists.objects.values_list('product_id', flat=True).filter(user=logged_user_id)

    for product in users_products_in_watchlist:
        watchlist_array.append(product)
        if int(listing_id) == int(product):
            display_remove_button = True



    # if listing_id in Watchlists.objects.filter(user=logged_user_id):
    #     display_remove_button = True
    # else:
    #     display_remove_button = False

    # This stores the 1st half of the currently selected product's URL
    listing_url_1st_half = "listing/"

    # This stores the full URL for the currently selected product
    product_page_complete_url = listing_url_1st_half + listing_id

    # This executes if the user clicks on "Add to Watchlist"
    if request.method == "POST":

        # This prepares the Query Set statement for inserting the product into the Watchlist table
        add_to_watchlist = Watchlists(user=user_instance, product_url=product_page_complete_url)
        add_to_watchlist.save() # This saves the entry into the database

        # This will add the product's ID into the Watchlist database
        add_to_watchlist.product_id.add(current_listing_instance)

        # This will reload the current page, so that the button changes without having to exit the page
        return HttpResponseRedirect(f"/listing/{listing_id}")


    # This renders the selected listing
    return render(request, "auctions/listing.html", {
        "current_listing": current_listing,
        "seller": seller,
        "current_listing_id": listing_id,
        "watchlist_array": watchlist_array,
        "display_remove_button": display_remove_button
        # "users_products_in_watchlist": users_products_in_watchlist
    })