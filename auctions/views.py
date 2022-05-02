from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

# This will let me find the max value from a list of database entries
from django.db.models import Max

""" This will let me obtain the current date and time whenever I create a listing (source: 
https://pythonguides.com/how-to-get-current-time-in-django/ )
"""
import datetime

""" This will let me use the "@login_required" attribute (source: 
https://docs.djangoproject.com/en/4.0/topics/auth/default/#the-login-required-decorator )
"""
from django.contrib.auth.decorators import login_required

"""  This will let me use the Django form for creating listings, which is on the forms.py file (source: 
https://docs.djangoproject.com/en/4.0/topics/forms/ . I'm also adding the form that allows me to get the bids from
buyers. )
"""
from .forms import CreateListingForm, BidForm, CommentForm

from .models import User

# This will import the Listings,Categories, and all the other tables from the models.py file
from .models import Listings, Categories, Bids, Comments, Watchlists

""" 
I can show the active listings in the home page, regardless of whether the user has logged in or not. Remember 
that you don’t have to be logged in in eBay in order to see a product and their price. You only need to log in to buy 
or sell a product.

I need to send all of the resulting data into index.html, NOT to create.html. I want to display the listings on 
the home page, NOT on the page for creating a new listing. So, I’ll need to specify that on the views.py file.

BUG: The prices aren’t being updated properly on the Active Listings nor in the Closed Auctions pages.

To solve this, I need to put the same Jinja code that I put on listings.html on index.html. Also note that I will need 
to copy and paste the code that gets the highest bid from the display_listing() view into the index() view. I also need 
to add the variables that will get the bids from the database so I can send them over Jinja to index.html.

I will have to do the same in the inactive_listings() view and the inactive.html file.
	
I have a massive problem, which is that I need to get the number of bids for each of the products. So, I think I should 
do like for the watchlists: create an array that will store all of the bids for each of the products during each 
iteration of the “for” loop that will render each product. But even this could give me problems, since all of the 
bids for all of the products would be stored in the same array, which would give me all kinds of problems.

Another possible solution would be to either take either the highest bid amount or the initial price for a product from 
the database, depending on the case.

I think that the key for displaying the prices correctly in Active Listings is storing all of the price amounts in an 
array. I will first declare an empty array. Then, I will create a “for” loop that will iterate every product that’s 
active. Then, I will check if there’s at least one bid for the current product in the “for loop” (or check if it’s not 
0 or not none. I don’t know how the max() function works.) If the current product in the loop has at least a bid, I 
will append the maximum bid for that product in an array using the max() function. That will give me a number, not an 
instance, so it will work. If that product doesn’t have at least a bid, or the max function returns 0 or None, I will 
append the price from the initial_price column from the Listings table into the array.  

Then, I will send that array via Jinja to the Active Listings page (index.html). Finally, I will create a “for” loop on the index.html file, and I will iterate every item of the price array in the HTML tag that has the “Current Bid” title. But, to avoid bugs, I need to get this loop and the “Current Bid” title out of the “for listing in listings” loop. Otherwise, it will print me more than once each price of each product. I will have to create twice the “for listing in listings” loop to prevent nesting the “for” loop that iterates the “price amount” array inside of the previous loop.

To a number as a maximum value using Max(), I will have to use an associative array style of notation. For instance, I 
could use notation like the following: 
max_variable = Table.objects.aggregate(Max('column'))['column__max'] 
(source: afahim’s reply on https://stackoverflow.com/questions/844591/how-to-do-select-max-in-django )

"""
def index(request):

    # This stores all the active products
    listings = Listings.objects.filter(active=True)

    # This is the declaration of the variable that will display the amount for the highest bid
    highest_bid_amount = ''

    # This array will store all the price amounts for each product
    price_amounts_for_all_products = []

    # This will store the price for each product in the array that stores the prices
    for product in listings:

        # This gets all the bids for the current product in the loop
        bids_current_product = Bids.objects.filter(listing=product.id)

        # This gets the highest bid for the current product in the loop
        highest_bid_amount = bids_current_product.aggregate(Max('bid'))['bid__max']

        # This checks if the product has any bids
        if highest_bid_amount is not None:
            # This inserts the highest bid for the current product in the prices array
            price_amounts_for_all_products.append(highest_bid_amount)

        # If the product doesn't have any bids, I will print its initial price
        else:
            price_amounts_for_all_products.append(product.initial_price)


    return render(request, "auctions/index.html", {
        "listings": listings,
        "price_amounts_for_all_products": price_amounts_for_all_products,
        # "highest_bid_amount": highest_bid_amount,
    })

""" This will display all of the closed auctions

"""
def inactive_listings(request):
    return render(request, "auctions/inactive_listings.html", {
        "listings": Listings.objects.all(),
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

    logged_user = request.user      # This stores the data from the currently logged in user
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

BUG Fix: The "Add to Watchlist" button doesn't change to "Remove" immediately after adding a product to that user's watchlist.
Instead, I have to exit the currently selected product's page, and the re-enter it so that I can notice the difference.
So, I will try reloading the current page by using HttpResponseRedirect.

BUG Fix: If the user’s not logged in, I get an error message from Django saying "User matching query does not exist" whenever 
I try to enter into a product’s page. To fix it, I will try to use the function “request.user.is_authenticated” to check 
if the uer’s logged in before trying to insert their ID into the variable that I’m using to store it (source: 
https://www.delftstack.com/howto/django/django-check-logged-in-user/#:~:text=Check%20the%20Logged%20in%20User%20in%20Views%20in%20Django,-In%20views%2C%20we&text=We%20can%20use%20request.,in%2C%20it%20will%20return%20True%20. )

Now, I will need to remove the product from the user’s watchlist if they click on “Remove”, by removing that entry from the 
database. To do that, I will create a new input for the forms that have the “Add to Watchlist” and “Remove” buttons, 
respectively. That new input, which will be hidden, will have their “name” attribute to have different values, so that the 
views.py file can differentiate between the “Add” and the “Remove” buttons whenever a user clicks on them. For instance, I can 
add “ name=’add’ ” for the “Add” button, and “ name=’remove’ ” for the “Remove” button. 

Then in the display_listing() view, I will put an “if” statement that checks if the “add” or the “remove” buttons were pressed. 
If the “add” input was submitted, I will insert that product into the watchlist. Meanwhile, if the “remove” button was submitted, 
I will delete that entry from the database. I need to check how to delete an entry from a database by using Query Set notation.

An alternative method would be to use the same “name” attribute for both the “Add” and “Remove” inputs. Then I would check on the 
display_listing() view the value of the input. If the input’s value is “Add to Watchlist”, I will execute the Query Set statements 
to add that product into the user’s watchlist. Otherwise, if the input is “Remove from Watchlist”, I will execute the Query Set 
statements to remove that entry from the user’s watchlist in the database.

To delete a record from a database by using Query Set notation, I need to use the following function: 
“Table.objects.filter(id=id).delete()” (source: Wolph’s reply on 
https://stackoverflow.com/questions/3805958/how-to-delete-a-record-in-django-models .)

Users should be able to see the bid form from the listing.html page (the page that displays the currently selected 
product.) So, there’s no need (and I shouldn’t) create a new view. I should use a currently existing view(), which, in 
this case, should be the display_listing() view. I will import the bid form into that view, and send it via Jinja to 
listing.html.

However, the only users who should be able to bid should be logged users. The assignment even says “If the user is 
signed in, the user should be able to bid on the item”. So, I should use the function that says that, if the user’s 
signed in, that the user should be able to see the bid form.

Also, I will have to insert the bid amount into two tables: The Bids table, and the Listings table. I need to update 
the price of the product after someone makes a bid, so the Listing table needs to be updated. Also, since it seems 
that one of the questions of this homework assignment asks me to show a page with all of the bids made by a user, I 
will need to keep track of that user’s bids. That can be done by inserting the bids on the Bids table.

Now, to detect whether I clicked on either “Bid” or “Add to Watchlist”, I will go the display_listing() view, and I 
will use the following line of code to detect which submit button I clicked: "if 'post_form_name' in request.POST:"  
(source: Damon Abdiel’s reply on 
https://stackoverflow.com/questions/866272/how-can-i-build-multiple-submit-buttons-django-form .)

Next, I need to add the code that will be executed if the user clicks on the “Bid” button. I will insert whatever 
number is inserted in there into the database on the Bid table. But, for debugging reasons, I could add a message to 
be printed if the user clicks on “Bid.”

The 3 columns to which I need to insert in the Bid model whenever a user bids for a product are “listing”, “buyer”, and “bid”. 
Both “listing” and “buyer” are foreign keys. But still, I need to get the proper user and product ID, and insert them into 
“listing” and “buyer”, respectively. I will get the user ID from “request.user”, since I need the ID of the user that’s currently 
logged-in, and I need to insert it into “buyer”. As for the “listing” column, I will get the ID of the product that’s being 
displayed in the current page. That’s stored in the 2nd parameter of the display_listing() view (listing_id).

Finally, for the “bid” column, I will get the number that was typed on the “Your bid” input from the POST form. However, I need 
to put a set of conditions on it. The user won’t be able to just type any number as the price for their bids. They will have to 
type a bid that’s equal or higher than the initial bid. Additionally, if another user had already placed a bid on that product, 
then the current user needs to place a bid that’s larger than the previous user. It wouldn’t make sense if a current user can 
buy the product if they place the same bid as a previous user who had previously bidded on that item. So, if the current user 
places a bid larger or equal to the initial bid, and larger than any other previous bid from other users, their bid will be 
inserted into the Bid model in the “bid” column.

Otherwise, I need to display an error message saying that the bid needs to be higher than any other previous bid, and the bid 
that was entered in the input box shouldn’t be inserted into the database.

The thing is, I need to be able to differentiate between the initial price and if at least someone else has already placed a 
bid for a particular product. Otherwise, the “if” statement won’t be able to tell the user if they are able to place a bid 
that’s exactly the same as the price for that product (the initial bid), or if they are forced to place a bid that’s higher 
than the price that’s being shown on the page (in the case that another person has already placed a bid on that item).

One way to tell my “if” statement if the user can enter a bid that’s equal to the price being displayed is by checking the Bid 
table to see if there’s any entry that has the ID of the product that’s currently being displayed on the page. If that product 
doesn’t have any entry on that table, then the prices being shown on the page is the initial bid. So, the user will be able to 
place a bid that’s the same (or higher) than the one being displayed on the page. Otherwise, if there’s at least 1 entry on the 
Bids table for that particular product, they user will not be able to place a bid that’s equal to the price being diplayed on 
the page. They will only be able to enter a price higher than the one from the bid placed by the previous user. 

Also, the current user will be able to tell if someone has already placed a bid for that product since the page will display the 
name of the bidder that had placed the previous bid. That way, the user will be able to tell if they can place a bid that’s 
equal to the price being displayed or not.    

* Note for a future algorithm: once I get all of the bids that have been placed for a specific product, and if the seller wants 
to close the auction for that item, I will use a Query Set statement that gets all of the bids from the Bid model for that 
product. Then, I will obtain the bid that has the highest value for the “bid” column. I could use something similar to the 
“MAX” function from SQL. Then, that would be the winner for that auction.

Remember: I cannot insert anything on any of the 3 columns for the Bids table unless all of the conditions from the “if” 
statement are met.

To check whether a person has placed a bid on an item, I will count the number of entries for the Bids table for the currently 
selected product. If it’s 0, then nobody has placed a bid on the current product. Otherwise, at least someone has bidded on the 
product. To count the number of entries in a table by using Query Set, I need to use the following format: 
variable = Model_name.objects.filter(column=what_youre_looking_for).count() (source:  Mikhail Chernykh’s reply on 
https://stackoverflow.com/questions/15635790/how-to-count-the-number-of-rows-in-a-database-table-in-django .)

To avoid any issues when comparing numbers, I will make sure to convert the numbers obtained from the database and the post 
form into floats. That can be done with the float() function (source: 
https://www.datacamp.com/community/tutorials/python-data-type-conversion .)

Now that the display_listing() view is properly detecting the amount typed by the user on the bid input, I need to 
modify the database properly by adding entries into the Bids table, and modifying the “initial_price” column of the 
Listing table with the bid of the current user. If the user types any appropriate bid amount, I will always add an 
entry on the Bids table. It doesn’t matter if the same person bids multiple times for the same product, as long as 
their current bid is higher than their previous one. I will also update the “initial_price” column of the Listings 
table every time that the user types an appropriate bid.

The only thing that I need to pay attention is that, if at least 1 user bids on an item, I will display their name on 
the page. I will put something like “Current highest bidder: (Name.)” 

To add an entry on the Bids table with the bid placed by the user, I will use a Query Set statement that says “insert 
the ID of the currently logged in user and of the product of the current page in the ‘buyer’ and ‘listing’ columns. 
Then, insert the bid from the POST form in the ‘bid’ column.” I may not need to use the “column_name.add(variable)” 
snippet of code since I’m using foreign keys, not Many to Many relationships. That is, after typing “.save()”, the 
query should add the entry into the Bids table.

Next, I would have to update the “initial_price” column from the Listings table with the amount from the current bid. 
I think that a Query Set statement similar to the one in the previous paragraph would work. The only thing that would 
change would be the column that I should use. 

Actually, I’m wrong: I can’t use the same Query Set for inserting an entry into a table for updating the column of an 
entry. I need to specify first the exact entry that I want to modify (like by using the “filter” attribute), and then 
I can update that entry.

To update an entry using Query Set, I need to use the update() function. I would need syntax like the following: 
Model_name.objects.filter(pk=id_of_entry_I_want_to_modify).update(column='new_value_for_column') 
(source:  Daniel Roseman’s reply on 
https://stackoverflow.com/questions/2712682/how-to-select-a-record-and-update-it-with-a-single-queryset-in-django )

BUG FIX: to add an entry into the Bids table, I needed an instance of the Listing class to insert the ID of the 
current product into the “listing” column (I guess because it’s using a foreign key). That’s done using a Query Set 
with get(), and inserting that into a variable.

Now, I want to display the name of the bidder for the person who placed the previous bid (if at least one person has 
bidden for the current product.) For that, I need to call the “buyer” column of the Bids table (using syntax like 
“bid.buyer” via Django.) But the thing is that I need the name of the person who has the highest bid. I need to look 
for a Query Set that gets a maximum value from a list of entries for a table (like MAX did in SQL.)

Or, since the maximum bid is the same as the value in “initial_price” on the Listings table, I could check if there’s 
at least 1 bidder in the Bids table for the current product. If there is, I will check the ID of the bidder for the 
current product that has bidden for the price being shown on the page (which is stored in the “initial_price” column.)

I will create an empty variable at the start of the display_listing() view, which will store the name of the highest 
bidder for the current product. It will be initially empty. Then, I will check what I specified in the last paragraph. 
If I find a bidder, I will store the name of that bidder in a variable, and send it to listing.html to print it.

The part of making the list inactive once the seller clicks on a button on their own listing can be relatively 
simple to do. The problem will be choosing the highest bidder and setting them as the winner of the auction.

So, I will first turn the product for a particular listing to become inactive when the seller presses a button to 
close the auction. If it’s inactive, I’m planning on hiding the listing from the “Active Listings” page.

To make the button clickable and make something happen to occur, I would need to use a “Submit” button by using a POST 
form. Remember to give a different ID to that submit button compared to the other buttons in the product page. That 
button will say something like “Close Auction”. Then, after the user clicks it, the views.py file will get that 
request, and do something. 

I could create a new view for adding the functionality that closes the auction if the seller clicks on the “close 
auction” button. 

Remember, only the seller should see the “close auction” button. So, I’ll have to put a condition saying that the user 
must be logged in by using the decorator that checks if a user is logged in on top of the “close auction” view. Then, 
I need to put an extra condition saying that the “close auction” button should only appear if the ID of the user is 
the same as the ID of the seller of that particular product.

After further consideration, I see that I SHOULDN’T create a new view for closing the auction. Otherwise, I would need 
to create a new URL, and add it on the urls.py file. And the thing is that I want to display all of this in the 
listing.html page. So, I will need to add the functionality for closing the auction inside of the display_listing() 
view.

The first important task will be to ONLY render the “Close auction” button if that product’s seller is logged in. I 
can do that by sending a variable from the display_listing() view to the listing.html file, and using an “if” 
statement in the listing.html file. I will check that, if the seller for the current product is logged in, I will 
render the “Close auction” button.

Now that I’m detecting if the user has clicked on the “Close Auction” button, I will need to change the property from 
the Listings model that says whether as listing is active. I will change it to False. The property is called “active”, 
I have to update it to False. I need to use a Query set statement.	

Now, to make the highest bidder the winner of the auction, I will first get from the database who’s the highest 
bidder. Then, I will display their name once they win the auction. This will be relatively complicated, since I need 
to get the data from the Bid model to get the bidder with the highest bid.

For debugging purposes, I will store the name of the auction winner in a variable, and print it on the listing page.

To make the homework assignment easier, I will create a separate page that will display the closed listings. That way, 
I’ll be able to easily find closed listings (since they should disappear from the “Active Listings” page), and I’ll 
be able to easily display a message to the highest bidder telling them that they won the auction (if they enter into 
that product page.)

But first, before creating a new page and a new URL, I will show the auction’s winner a victory message if they are 
logged in in the closed listing’s page. I will need to compare the name of the currently logged in user, and the name 
of the auction’s winner. If they are the same, I will display the victory message. The column of the User model that 
stores the names of the users is “username”.

I will later also need to display all of the comments stored in the database within the current product page. But, 
to do that, I will need to modify the display_listing() view to be able to get the comments from the POST form, and 
store them on the database. THEN I will send the comments via Jinja to the current product page (the listing.html 
file.)

BUG: If I edit a bid from the admin panel, and then I enter into that product’s page on the web app, I get the 
following error: “DoesNotExist at /listing/3. Bids matching query does not exist.” I think that happens because I’m 
getting the bid by using a query by the amount of money, not from the bid’s ID. I need to fix that. 

To fix the above bug, I will fix my code so that, to look for the highest bid, I will use a function that gets the 
maximum value out of all of the bids for a particular product. I can do that by importing a library called “Max”. Then, 
I will obtain all of the bids for a particular product using filter(). After that, I will get the max bid value by 
using the following function: aggregate(Max(‘column’)). Finally, to get the instance of the bid with the highest value, 
while also accepting empty values (if nobody has bid for a particular product), I will use the following snippet: 
instance = variable.order_by(‘-column’).first() (source: Sasha Chedygov’s reply on  
https://stackoverflow.com/questions/844591/how-to-do-select-max-in-django .)

BUG: Even if I delete a bid, a product will never return to its original price, and it won’t return to its previous 
lower bid either. That is, if a product is worth $70, and someone bids $79 for it, even if I delete that bid, the 
price will still charge you $79. It will never go back to its original $70 price. I need to fix this. 

As to how to return to the original price if the bid deleted was the only bid, I will need to store the initial price 
somewhere else in the database. For instance, I could create a new column called “current_price” for the Listings 
table. That column will have the exact same value as “initial_price” if no one has bid for that product (or if all of 
the bids for that product have been deleted.) However, I might have to delete and rebuild the database for this to 
work properly.

I need to look at the code from the display_listing() view to see where I’m getting the current price of the product 
that I’m displaying on a product page. I need that price to be equal to the highest bid stored in the database.

The problem may be the line “<b>Current Bid:</b> ${{listing_data.initial_price}}”. I shouldn’t take the price of the 
bid from the initial_price column from the Listings table. I need to take the max value for the “bid” column for 
the Bids table.

I could create a condition saying that, if there are no bids, display the price stored in “initial_price”. I will 
modify my code so that initial_price is never modified (so that I could always get the initial price if I delete all 
of the bids.) But, if there are bids, that the price that should be displayed should be the max value for the “bid” 
column from the Bids table.

To detect if there’s at least a bid, there are multiple ways. I could say that, if the variable that stores the highest 
bid amount is not empty, that the current bid displayed on the page should be the variable that contains the highest 
bid. Otherwise, I should display the price stored in “current_price”.

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

    # This imports the form that will store the bids
    bid_form = BidForm()

    # This imports the form that stores the comments
    comment_form = CommentForm()

    # DEBUGGING message that will show up if the user clicks on "Bid"
    debugging_message_bid_button = "You didn't click on the 'Bid' button."

    # Confirmation or error message for bids
    bid_message = ''

    # This gets the price of the product of the current page
    current_product_price = current_listing_instance.initial_price

    # This checks the number of bids that have been placed for the current product, if any
    number_of_bids = Bids.objects.filter(listing=listing_id).count()

    # This will tell the product page whether to render the "Close auction" button
    display_close_auction_button = False

    # Debugging message to check if I'm getting the active status from the Listings model
    debugging_message_active_status = "Nothing has happened."

    # This will check if the current listing is active
    is_listing_active = current_listing_instance.active

    # This will make the "Close Auction" button to be active if the seller hasn't closed the auction
    is_close_auction_button_active = True

    # This declares the variable that will store the name of the winner of an auction
    auction_winner_name = "Nobody has won the auction yet."

    # This declares the variable that will store the victory message for the winner of an auction
    victory_message = ''

    # This is the declaration of the variable that will display the amount for the highest bid
    highest_bid_amount = ''

    # This takes the highest bidder from the Bids model
    highest_bidder_id = "No one has bid for this listing yet."
    if number_of_bids > 0:

        # This stores an instance of a bid where the amount bid is equal to the price displayed on the product page ...
        # highest_bid_instance = Bids.objects.get(bid=current_product_price)

        # This obtains all the bids for the current product
        all_bids_for_current_product = Bids.objects.filter(listing=listing_id)

        # This obtains the instance of the highest bid
        highest_bid_instance = all_bids_for_current_product.order_by('-bid').first()


        # This stores the name of the highest bidder
        highest_bidder_id = highest_bid_instance.buyer

        # This stores the highest bid as a price amount
        highest_bid_amount = highest_bid_instance.bid

        # This will print the name of an auction's winner
        if highest_bid_instance.is_auction_winner:
            auction_winner_name = highest_bidder_id


        # This updates Bids table so that the highest bidder is inserted into the database 
        # Bids.objects.filter(bid=current_product_price).update(is_auction_winner=True)

    # This will check the database to decide whether to activate the "Close Auction" button
    if is_listing_active:
        is_close_auction_button_active = True

        debugging_message_active_status = "This listing is currently active."

    else:
        is_close_auction_button_active = False

        debugging_message_active_status = "This listing is NOT active."

    # If the user is logged in, I will store their ID
    if request.user.is_authenticated:
        logged_user = request.user      # This stores the data from the currently logged in user
        logged_user_id = logged_user.id     # PK of the currently logged in user

        # This stores the username of the user that's currently logged in
        logged_user_username = logged_user.username

        # This creates an instance of the User table, which I'll need to use in the Query Set syntax
        user_instance = User.objects.get(id=logged_user_id)

        # This stores the seller ID of the current product
        current_product_seller_id = current_listing_instance.seller_id_id

        # This checks if the current user is the seller of the current product
        if logged_user_id == current_product_seller_id:

            # If the condition applies, I will render the button
            display_close_auction_button = True

            # This executes if the user clicks on "Close Auction", and closes the auction
            if 'close_auction' in request.POST:

                # This sets the current listing to become inactive
                Listings.objects.filter(pk=listing_id).update(active=False)

                # This disables the "Close Auction" button
                is_close_auction_button_active = False

                # This stores the winner of the auction
                # auction_winner_name = highest_bidder_id

                # This updates Bids table so that the highest bidder is inserted into the database 
                Bids.objects.filter(bid=current_product_price).update(is_auction_winner=True)

        # This will check if somebody won the current auction
        if auction_winner_name != "Nobody has won the auction yet.":
            
            # This will check if the winner of the auction is currently logged in
            if str(auction_winner_name) == str(logged_user_username):

                # This will print a message telling the auction's winner that they won the auction
                victory_message = "Congrats! You have won the auction for the current listing."

            # DEBUGGING message
            else:
                victory_message = "Sorry. You're not the winner of this auction."

        # This array will store all the products from a user's watchlist
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
        if 'submit_add_or_remove' in request.POST:

            add_or_remove = request.POST["add_or_remove"]

            if add_or_remove == "add":

                # This prepares the Query Set statement for inserting the product into the Watchlist table
                add_to_watchlist = Watchlists(user=user_instance, product_url=product_page_complete_url)
                add_to_watchlist.save() # This saves the entry into the database

                # This will add the product's ID into the Watchlist database
                add_to_watchlist.product_id.add(current_listing_instance)

            if add_or_remove == "remove":
                remove_message = "DEBUGGING MESSAGE: Remove from database"

                # This deletes the current product from the watchlist
                Watchlists.objects.filter(product_id=listing_id).delete()

            # This will reload the current page, so that the button changes without having to exit the page
            return HttpResponseRedirect(f"/listing/{listing_id}")

        # This checks if the "Bid" submit button was pressed
        elif 'submit_bid' in request.POST:
            debugging_message_bid_button = "Great! You clicked on the 'Bid' button!"

            # This stores the submitted bid on a variable
            submitted_bid = request.POST["your_bid"]

            # This checks if the user placed a bid that's equal or higher than the price shown on the product page
            if float(submitted_bid) >= float(current_product_price):

                # This checks if there's at least one bid in the Bids table
                if number_of_bids > 0:

                    # This checks if the current bid is greater than the previous one
                    if float(submitted_bid) > float(current_product_price):
                        debugging_message_bid_button = "Good! Your bid is greater than the one placed by someone else."

                        bid_message = "Your bid has been successfully registered!"

                        # This inserts the bid into the Bids table
                        insert_bid_into_bids_table = Bids(buyer=user_instance, listing=current_listing_instance,
                                                          bid=submitted_bid)
                        insert_bid_into_bids_table.save()  # This saves the entry into the database

                        # This modifies the price of the product on the Listings table
                        # Listings.objects.filter(pk=listing_id).update(initial_price=submitted_bid)

                    # If the current bid is the same as the previous bid, I'll show an error message
                    elif float(submitted_bid) == float(current_product_price):
                        debugging_message_bid_button = "Sorry, but you need to place a bid that's higher than the previous one."

                        # Error message
                        bid_message = "Sorry, but you need to place a bid that's higher than the previous one."

                # This checks if there are no bids on the Bids table
                elif number_of_bids == 0:
                    debugging_message_bid_button = "Awesome! You're the first person to bid on this product!"

                    # Confirmation message
                    bid_message = "Your bid has been successfully registered!"

                    # This inserts the bid into the Bids table
                    insert_bid_into_bids_table = Bids(buyer=user_instance, listing=current_listing_instance,
                                                      bid=submitted_bid)
                    insert_bid_into_bids_table.save()  # This saves the entry into the database

                    # This modifies the price of the product on the Listings table
                    # Listings.objects.filter(pk=listing_id).update(initial_price=submitted_bid)

            # This tells the user that they need to place a bid that's at least as high as the one displayed on the page
            else:
                debugging_message_bid_button = "Sorry, but you need to place a bid that's at least as high as the one currently listed."

                # Error message
                bid_message = "Sorry, but you need to place a bid that's at least as high as the one currently listed."

    
    # Ths will prevent any bugs that won't let me show a product's page if I'm not logged in
    else:
        watchlist_array = []
        display_remove_button = False

    # This executes if the user clicks on "Comment"
    if 'submit_comment' in request.POST:

        # This gets the comment from the POST form
        comment = request.POST["comment"]

        # This inserts the comment into the database, on the Comments model
        insert_comment = Comments(comment=comment, user=user_instance, listing=current_listing_instance)
        insert_comment.save()

    # This will obtain all the comments for the current listing
    current_listing_comments = Comments.objects.filter(listing=listing_id)



    # This renders the selected listing
    return render(request, "auctions/listing.html", {
        "current_listing": current_listing,
        "seller": seller,
        "current_listing_id": listing_id,
        "watchlist_array": watchlist_array,
        "display_remove_button": display_remove_button,
        "bid_form": bid_form,
        "debugging_message_bid_button": debugging_message_bid_button,
        "bid_message": bid_message,
        "display_close_auction_button": display_close_auction_button,
        "is_close_auction_button_active": is_close_auction_button_active,
        "debugging_message_active_status": debugging_message_active_status,
        "highest_bidder_id": highest_bidder_id,
        "auction_winner_name": auction_winner_name,
        "victory_message": victory_message,
        "comment_form": comment_form,
        "current_listing_comments": current_listing_comments,
        "highest_bid_amount": highest_bid_amount
        # "logged_user_username": logged_user_username
        # "users_products_in_watchlist": users_products_in_watchlist
    })

""" This is the view for the Watchlist page. This is really similar to the index page, that is, the page that displays 
the active listings. The difference is that, instead of displaying all of the active listings, I will only display the 
products from the watchlist of the user that’s currently logged in.

The first thing that I need to do is to create the page that will display the Watchlists. I need to create the html 
file for the page. I will also have to include in the layout of the site (in layout.html) a link to the watchlists 
page, which will only be accessible users who have logged in. I will also need to add a link to the page in urls.py to 
the Watchlist page. Additionally, I will need to create a view function to display the watchlist. This needs to be 
done in the watchlist() view.
	
First, I need to store an instance of the user’s watchlist. This is done with Query Set’s get() function. Turns out I 
can't do this since each time that an user adds something to a watchlist, a new entry is created on the Watchlist 
table. So, I will have to use Query Set's filter() function, not get(). 

I will need to store all of the listing IDs from that watchlist into a variable, to have all of the products inside 
that particular watchlist in a single variable. Then, I will send that variable via Jinja to the watchlist page. 
Afterwards, I will use a “for” loop to print each element of that variable, which corresponds to every item in 
that person’s watchlist. 

That way, I’m getting the IDs of every product that belong to the logged user’s watchlist. Now that I have those IDs, 
I could go to the watchlist() view, and create another “for” loop. In this case, I want to compare the IDs of every 
product in the user’s watchlist to the product IDs from the Listings table. Then, if both IDs match, I will get that 
all of the data from those products where a match occurred. This, way, I will get all of the data from each product. 
Finally, I will send that to the watchlist.html page via Jinja, and print that information. 
	
The way that I’m going to print the information for each product in the user’s watchlist will be similar (if not the 
same) as I printed every product in the “Active Listings” page.   

"""
@login_required
def watchlist(request):

    logged_user = request.user  # Instance of the user that's logged in
    logged_user_id = logged_user.id  # ID of the user that's logged in

    # Instance of the logged user's watchlist
    # watchlist_instance = Watchlists.objects.get(user=logged_user)

    # This gets all the product IDs inside the currently logged user's watchlist
    watchlist_products = Watchlists.objects.values_list('product_id', flat=True).filter(user=logged_user_id)

    # This gets all the info from all the products in the active listings
    active_products = Listings.objects.filter(active=True)

    # This will get all the data from each product ...
    # for watchlist_product in watchlist_products:
    #     for product in active_products:
    #         if int(product.id) == int(watchlist_product):
    #             pass


    # watchlist_products = Watchlists.objects.filter()

    # DEBUGGING message: this is just to display the page
    # watchlist_products = "This is your watchlist."


    return render(request, "auctions/watchlist.html", {
        "watchlist_products": watchlist_products,
        "active_products": active_products,
    })

""" This is the view for the Categories page. 

For question 6 in general, I will need to create 2 pages: one for displaying all of the categories, and one for 
displaying all of the active listings for a specific category. For now, I will create the page that will only display 
the name of all categories.

So, since I need to create a new page, I need to create a view, a URL, and an HTML file.

Everyone will be able to access the categories page, even if they’re not logged.

Now, I need to get all of the categories from the Categories table, and store them in a variable. That can be done 
with Query Set’s filter() function, or with objects.all(), since I want all of the categories.
 
"""
def categories(request):

    # This will store all the categories from the Categories table
    category_list = Categories.objects.all()

    return render(request, "auctions/categories.html", {
        "category_list": category_list,
    })

""" This will show the page that displays all of the active listings for a specific category.

Once again, I need to create a view, a URL, and an HTML file. The URL should be similar to that as the one used for 
the display_listing() view, since there will be a different page for each specific category. The URL could be something 
like “/categories/1”, or “categories/Fashion”. The latter would make it easier for users to bookmark the page, or to 
type directly into the URL their favorite category. However, since I don’t know if I made unique each instance of the 
name of the category, I will play it safe and use the ID of each category, and display it in the URL. So, basically, I 
will make the URL for the specific categories really similar to the display_listing() view.

The page that shows all of the active listings for a specific category will be really similar to the index.html file 
(the Active Listings page.) In fact, it will be the same, except that it will only display the listings that belong to 
a specific category.

To obtain the specific category that the user typed or clicked, and check to which category that belongs in the 
database, I need to use the get() function from Query Set, and check that the ID is the same as the one typed as a 
parameter in the URL.

Now, I need to obtain all of the products in the Listings table that meet two requirements: that are active, and that 
belong to the category of the current page. To check that the two conditions are fulfilled, I could use an “if” 
statement. The columns that I want to check from the Listings table are “category” and “active”. And, since I will be 
obtaining multiple products, I will use Query Set’s filter() function. Now that I think about it, I can simply put the 
conditions in the filter() function without needing to use an “if” statement.

"""
def category_listings(request, category_id):

    # This will obtain the current category from the Categories table
    current_category_instance = Categories.objects.get(id=category_id)

    # This stores the name of the current category
    current_category_name = current_category_instance.category

    # This will store all the active listings for the current category
    products_in_selected_category = Listings.objects.filter(category=current_category_name, active=True)



    return render(request, "auctions/category_listings.html", {
        "current_category_instance": current_category_instance,
        "products_in_selected_category": products_in_selected_category,
    })