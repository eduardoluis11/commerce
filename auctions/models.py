from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

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

1.a) Listings:

For the listings model, I need the following fields: the username of the seller, the name of the product, the initial 
bid or initial price of the product, description of the product, date and time when the listing was created, URL of 
the image of the product (I will use only 1 image to make the homework assignment easier), and the auction category 
(like “video games” or “music”). Out of those 7 fields, only the username of the seller will be a foreign key, so I 
don’t have to add a character limit to that particular field. I will take the username from the “User” model.

Next, I will have to decide the character limit for each of the 6 remaining fields that aren’t foreign keys. 

For the description of the listing, I decided to first check what was the character limit for a listing description in 
eBay. It turns out that eBay allows you to put descriptions of up to 4000 characters (source: 
https://developer.ebay.com/devzone/merchant-products/catalog-best-practices/content/descriptions.html .) So, I could 
put a similar character limit for the listing descriptions of my web app. In my case, to make it a bit more original, 
I will put a character limit of up to 4500 characters for the listing descriptions in my app.

Next, for the comments, I decided that, instead of giving the user the option of posting questions or reviews, I will 
let them post comments in listings as if the listings were posts in social media or entries in a blog. That is, anyone 
can comment on a listing. I decided this since the assignment never said that I should put a question section to the 
listing. Also, reviews should only be able to be posted by people who had bought that particular product to that 
particular seller. So, to make this assignment easier, and since it doesn’t say otherwise, I will let any user 
comment anything on any listing.

Next, I checked an ideal character limit for URLs for the field that will store the URLs for the pictures. It seems 
that browsers such as Google Chrome can store URLs of up to 2048 characters (source: 
https://www.geeksforgeeks.org/maximum-length-of-a-url-in-different-browsers/ .) Therefore, I will give the “URL” field 
a limit of up to 2048 characters. 

For the rest of the fields, I will give them a random and relatively low number of characters as a character limit. 
For things like the title, I could give it a limit of between 200 and 300 characters. Or, I could use a limit of 64 
characters, like Brian did in this assignment’s lecture. I will only use the 64 character limit for the category. 
For the name of the product, I will put a limit of 128 characters (64 times two) since I think I’ve seen products on 
Amazon with titles longer than 64 characters.

For the initial price and the date and time when the listing was created, I will use the data type “Numeric”. It 
doesn’t make sense to store the date and time as an integer. As for the price, it will have decimals to indicate the 
cents of the price. So, once again, I can’t use integers. As far as I’m aware, I don’t have to specify a limit for 
“Numeric” data types.

Now, for the foreign key, I wanted to know how to import a foreign key in a model. Turns out that I need to use a 
function that has this syntax: “models.ForeignKey(foreign_key_field)" (source: felix001’s question on  
https://stackoverflow.com/questions/14663523/foreign-key-django-model .)

It would be best to first create the listing model before creating the bid and the comment ones, since the bid and 
comment models will directly depend on the Listing model, that is, I will use foreign keys to connect the Listing 
model to the Comment and the Bid ones.

Also, I will create a 4th model which will store the users’ watchlists. 

Since there isn’t “Numeric” as a model function in Django, I will have to use other data types to store the date of 
creation of the listing and the initial price. I will use “DateTimeField” to store the date and time, and 
“DecimalField” to store the initial price (source: https://docs.djangoproject.com/en/3.0/ref/models/fields/ .)

It turns out that, if I want to use DecimalField to store numbers, I need to specify the limit for the number of 
digits. In fact, I need to specify at least 2 arguments: the total digit size, and the decimal size. I want the decimal 
part to have a limit of 2 digits, since prices only have 2 decimals. However, I don’t want the prices in general to 
have a limit, so users can put bids of millions of dollars if they so desire. So, to do that, I will put the following 
parameters: max_digits=None, decimal_places=2 (source: https://www.geeksforgeeks.org/decimalfield-django-models/ .)
In the end, I got a bug telling me that I need to specify a limit to the number of digits for the price (it can't be
"None"). So, I added a limit of 12 digits: 10 for the "integer" part, and 2 decimal places. This way, sellers can 
set a price of up to $9,999,999,999,99 (or around 9 billion dollars.)

After further consideration, I won’t store the username of the seller into the “Listings” model. Instead, I will store 
the ID code assigned to them by the User model. That is, I will import the primary key of that seller from the User 
model. I will import it as a foreign key. It’s more efficient that way. I don’t have to store the username of the 
seller in “Listings” if it’s already being stored in “User”. I need to specify the property “CASCADE” if I delete the 
user’s ID code, since, otherwise, if a user creates a listing and I attempt to delete that user’s account, I will get 
an error message and I won’t be able to delete their account. I could call the field “seller_id”. I will rewatch 
Brian’s lecture to check how to assign “CASCADE” if I delete a field from a model in Django. After watching it, I see 
that I need to use “on_delete=models.CASCADE” as the 2nd argument of the ForeignKey() function.

As far as I understand, a foreign key is the primary key of the table that I’m importing data from. So, since the PK 
of the auction_user table is “id” (the ID code), the only thing that I will get from using the ForeignKey() function 
from the auction_user table is the ID code. I just have to specify the table’s name while calling ForeignKey() (or 
more specifically, the model’s name) as the 1st argument. Also, the ForeignKey() function is only used in one-to-many 
relationships (which is the case between the users and their respective listings.)

With regards to the relationship between the auction_listings and the auction_user tables, they will have a 
“one-to-many” relationship. That is because, even though 1 user can have multiple listings to sell different kinds of 
products, a listing should ONLY be able to be created by 1 specific user. So, I won’t use a many-to-many relationship.

I will set up a related name for the relationship between the sellers and their respective listings in case I want to 
know all of the products sold by that particular seller. This will be the third parameter of the ForeignKey() function 
for the Listing model. I will call it “list_of_products”.

For the date and time (or timestamp), I only want to store the date and time when the listing was created. I’m not 
interested at the moment to store the time when the listing gets modified in case the seller decides to modify it. So, 
the proper argument that I may need to use is “.auto_now_add” (source: 
https://docs.djangoproject.com/en/4.0/ref/models/fields/ .) More specifically, I need to type it the following way:
models.DateTimeField().auto_now_add (source: https://www.geeksforgeeks.org/datetimefield-django-models/ .)

Due to a bug that was showing up telling me that I couldn't create the Listing model if the fields didn't have 
a default value, I added a default value to all of the fields.

For the timestamp, I decided to forget about storing the current date and time here in models.py. I will only call 
DatetimeField() with some generic default value. Then ,on the form page, I will execute a SQL statement saying “insert 
today’s date in created_on (by using a function such as datetime.now())” (source:  Houman’s question on 
https://stackoverflow.com/questions/12030187/how-do-i-get-the-current-date-and-current-time-only-respectively-in-django 
.) For  the default value for the timestamp, I will use the following syntax for the date and time: '2022-1-1 1:00:00' 
(source: https://www.geeksforgeeks.org/datetimefield-django-forms/ .) 

I will add an extra field to the Listings model. I will store whether the listing is active or not. I don’t want to 
delete listings as soon as someone purchases that specific product. I want that listing to be archived, so that the 
seller of that listing is able to modify (or delete) that listing, or it at least remains archived in the web app. 
However, I don’t want anyone but the seller to access that inactive listing. I only want the active listings to be 
rendered to everyone on the website. So, to achieve this, I need to add an extra attribute to the listings table, 
which could be called “Active”, and could have values such as “True” or “False”.

Then, so that the inactive listings don’t show up to users when entering the website, I will execute an SQL query that 
says something like “SELECT * … WHERE active = True”.

Turns out that Django accepts boolean fields in its models. The field is called BooleanField() (source: 
https://docs.djangoproject.com/en/4.0/ref/models/fields/ .) So, I could add the field like this: 
models.BooleanField(default=”False”).

I will use the “__str__” notation for each class in the models.py file so that, when I use a “SELECT ALL” using 
Django’s API for working with databases, I get the name of each field for that table instead of getting 
“<querySet(number)>”. This way, it will be much easier to work with my database. After re-watching Brian’s lecture, it 
seems that the syntax that I need to use is the following: ‘def __str__(self): return f”{self.id}: {self.first_field} 
to {self.last_field}” ’. That must be just below the last field of the class in the model.

I need to use the strip() function somewhere else so that, in the dropdown menu, the parentheses, the commas, and the 
quotation marks disappear.

To fix the item names on the dropdown menu (so that it doesn’t display “cateogyr object(1/2/3/4)”), I needed to add a 
“__str__” snippet on the class that contains the Categories model, as Brian explained during the lecture.

I need to make the picture URL and the category columns to be optional in te Listings model. Otherwise, I can’t add 
any new listings from the Django panel if I don’t add any URL or text to any of those 2 columns. I can make a column 
to be optional if I use the property “blank=True” (source: Rohan’s reply on 
https://stackoverflow.com/questions/16828315/how-can-i-make-my-model-fields-optional-in-django .)

BUG: I can’t add any listings from the Django admin panel, since I get an error saying “AttributeError at 
/admin/auctions/listings/add/. 'str' object has no attribute 'utcoffset'”. I think the problem may be the date field 
from the Listings model (the “created_on” column). 

It seems that, to fix the above bug, I need to use “auto_now_add=True” instead of the “default” property of the column 
that contains a date (source: Carson Myers’ reply from 
https://stackoverflow.com/questions/2771676/django-datetime-issues-default-datetime-now ) 

I will have to create a new column for the Listings table, which will store the current modified price of the product. 
It will be called “current_listing”. I will remove the comments of the Query Sets that updated the initial_price 
column, but, instead of modifying the initial_price column, they will modify the current_price column. Then, I will 
add an extra condition in display_listing, index.html, and wherever saying that, if a product doesn’t have any bids, 
that current_price should be modified to be the same as initial_price. That should be done with an update() function 
through a Query Set statement in the index(), inactive_listings() and display_listing() views.

To fix the problem of the extra “s” letters appearing at the end of each table on the admin panel I will need to add an 
extra class on each model called “Meta”. Then I will have to use the following notation inside that class:
verbose_name_plural = "table_name_as_I_want_it"
(source: Abhyudit Jain’s reply from  
https://stackoverflow.com/questions/32047686/how-can-i-remove-extra-s-from-django-admin-panel .)

"""
class Listings(models.Model):
    seller_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="list_of_products", default=0)
    product_name = models.CharField(max_length=128, default='Product Name')
    description = models.CharField(max_length=4500, default='')
    picture_url = models.CharField(max_length=2048, default='', blank=True)
    initial_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    current_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_on = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=64, default='None', blank=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product_name} - ID: {self.id}"

    class Meta:
        verbose_name_plural = "Listings"

""" 1.b) Bids:

The three main fields that the Bids model will have will be the following:
    1-) The Listing table’s PK (via a “Foreign key” ** from Listings.)
    2-) The bid made by the buyers.
    3-) The buyer’s name or PK (via a “Foreign key” ** from User.)

** The reason I put “Foreign Key” between quotation marks is because I will need a many-to-many relationship between 
the bids and the listings (that is, between the Listing and the Bid models.) Foreign keys are for one-to-many 
relationships. So, I can’t use foreign keys in here. I will have to use the ManyToMany() function to import the 
Listing table’s PK. I need to rewatch Brian’s lecture to see how he used the Many-to-Many() function.

I will use a many-to-many relationship between the listings and the bids since one buyer can bid in multiple listings 
(to buy multiple products), and one listing can have many bidders (in fact, the bidder who offers the highest amount 
of money wins the auction.) So, using a one-to-many relationship for this case would be inappropriate.

After watching Brian’s lecture, I think I see how to call the ManyToManyField() function. To make the call to the 
ManyToMany() function, I need to use syntax like the following: “models.ManyToManyField(table_that_I_want_to_import, 
blank=True or False, related_name=’easy to remember name’)”. In my particular case, I want “blank” to be True in order 
to allow the listing to have 0 bidders (if nobody has yet put a bid on that product.) As for “related_name”, I want 
an easy to remember name so that I can make a reverse search if I have the listing or the buyer’s ID, but I want to 
search for all of the bids made by that person.

I will re-read the assignment to see what I need to store in the “Bids” model. Do I need to store all of the buyers’ 
information, or do I need to store how many bidders want to buy a product in a particular listing? Since it’s 
pointless to make separate tables for buyers and sellers since all of the info for all of the users are being stored 
into the Users model. So, I will store how many bidders want to buy a specific product for a specific listing. 

Even so, the relationship is kept as a many-to-many relationship, since one bidder could bid for multiple products at 
the same time, and one product can have multiple bidders.
    
Another thing that I may need to store in the “Bids” model is the winner of the auction, or, at the very least, 
store who the highest bidder is for a particular listing. So, I would have 4 fields in total: 1) PK of the bidder, 
2) bid of the buyer, 3) PK of the listing, and 4) the highest bid (that is, the highest amount of money offered .) 

I may choose between storing ALL of the bids made for 1 particular listing in the Bids table. However, the most 
important bid is the one made by the bidder who’s offering the highest amount of money. The amount of money of the 
highest bid should be the one being displayed on the website.
    
I think that the Bids model will basically be an intermediate table that will connect the users with the listings. 
That is, it will be comprised of mainly PKs of “foreign keys”. It will connect buyers with listings.

After further consideration, due to the use of “foreign keys”, I think that no entry on the Bids table could be NULL 
(or empty). Even the amount of money being offered by each person and the highest bid made will have to have a value 
other than NULL. It can’t be empty. So, I will give them all a generic default value, but I won’t use the 
“blank=True” property.

I could put extra restrictions (either here or further in the assignment) to specify that the bid cannot be lower 
than the product’s initial price set by the seller.

Now, I need to think about the character limits that I need to put on the bids and the highest bid for a particular 
listing. They will have the exact same restrictions as the one that I gave to the initial price set by the seller to 
a listing. That is, it will be a decimal field with up to 2 decimals, and it will have a total of 12 digits (10 
“integer” digits, and 2 decimals.)

Upon further consideration, do I really need to store the current highest bid for a listing? I could simply use an SQL 
statement to look for all of the bids, and only show the highest bid made using an SQL filter such as “Max”. Then, I 
would print that in the listing page. There’s no need to add a field to store the current highest bid. So, I will only 
leave the initial 3 fields for the Bids model.

After further consideration, I realized a mistake in the relationships. There isn't a single many-to-many relationship 
in the Bids model. For the relationship between bids and listings, a listing could have multiple bids, but one specific 
bid can only belong to one specific listing. So, there was a one-to-many relationship between listings and bids. And 
something similar occurs between users and and bids: one user can make multiple bids, but one specific bid can only 
belong to one specific user. So, there's also a one-to-many relationship between bids and users. Therefore, I need 
to use the ForeignKey() function for calling the PK of both the listings and the users. I shouldn't use the 
ManyToManyField() function.

I think I will need to modify the Bids model to store the winner of the auction. I need to keep a permanent record of 
the winner of an auction, so I will need to insert that information into the database. Since each entry in the Bids 
table already has the name of the bidder, I could add a Boolean column that will store whether the current bidder is 
the winner of that auction. It will be “False” by default. But, if the seller closes the auction, I will update the 
highest bid to have the column that indicates whether that user has won the auction to “True”.  

"""
class Bids(models.Model):
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="bids_from_listing", default=0)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids_from_user", default=0)
    bid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_auction_winner = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id}: ${self.bid} from {self.buyer} in {self.listing}"

    class Meta:
        verbose_name_plural = "Bids"

""" 1.c) Comments:
Since comments on a listing in my web app will be the equivalent of comments in a blog entry, I decided to look up 
Wordpress’ character limit for comments, since Wordpress is commonly used for creating blogs. Turns out that you can 
decide the character limit. However, according to a website I visited, comments in Wordpress sites should ideally be 
of up to 5000 characters (source: https://www.wpbeginner.com/wp-tutorials/how-to-limit-comment-length-in-wordpress/ .) 
So, by following this guideline, I decided that the character limit for comments on the listings in my app will be 5000 
characters.

I will let any user comment in any listing, whether they have placed any bids or bought anything or not.

Since one user can comment on multiple listings, and a single listing can have multiple comments, there is a 
many-to-many relationship between comments and users. Not only sellers will be able to comment, but buyers as well. I 
want to display the username of buyers and/or sellers on the comments, so I decided that I will add a field that stores 
the ID code of the people who comment. This is done with the ManyToManyField() function.

After further consideration, I realized that the above statement is incorrect. One user may be able to make many 
comments, but one specific comment can only belong to one specific user. So, there’s a one-to-many relationship between 
comments and users.

Also, there will be a relationship between comments and listings. This is done so that comments are actually printed on 
the proper listing. Since 1 listing can have multiple comments, but one specific comment can only belong to one 
specific listing, then there’s also a one-to-many relationship between comments and listings.

Therefore, for both the relationship between comments and listings, and the relationship between comments and users, 
I will use the ForeignKey() function.

So far, the main fields for the Comments table will be the following:
    1-) The comment itself.
    2-) The ID of the user who made the comment.
    3-) The ID of the listing where the comment was posted to.

Now, I have to decide the character limit for the fields for the Comments model. The only field to which I can assign 
a character limit is the comment itself. As I already specified above, the character limit for comments will be 5000 
characters.
"""
class Comments(models.Model):
    comment = models.CharField(max_length=5000, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments_from_user", default=0)
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="comments_from_listing", default=0)

    def __str__(self):
        return f"{self.id}: {self.comment}"

    class Meta:
        verbose_name_plural = "Comments"

""" 1.d) Watchlist:

I decided to create an optional 4th model, which in this case will be used for storing watchlists. Here, I will store 
the wish lists of each user (if they decide to store a product or listing into a wish list.)

The fields that I would need for the watch list would be the following:
    1-) The user’s PK.
    2-) The listing’s PK.
    3.-) The listing’s URL to its store page.

I need the URL of that product’s page since I will need to call it so that I can create a link to that listing. Then, 
if the user clicks on that link, they will be able to enter into that listing’s page.

Now, I need to check the relationships between the watchlist and the users, and between the watchlist and the listings. 
One user can only have 1 watchlist, but many users can have their own watchlist. But the thing is that, I’m not storing 
watchlists: I’m storing URLs. So, one user can store many URLS, and the same URL can belong to many different users. 
So, there’s a many-to-many relationship between the listing URLs and the users. Now, between the product URLs and the 
products themselves, a specific listing can have only one specific URL, and a specific URL can only have one product 
associated with it. So, there’s a one-to-one relationship between listings and their respective URLs. It turns out that 
Django has a form field for one-to-one relationships, which is the OneToOneField() function (source: 
https://docs.djangoproject.com/en/4.0/ref/models/fields/ .) I need to specify “on delete cascade”, and it’s recommended 
that I specify a related_name attribute. So, I need to use syntax like the following: 
models.OneToOneField(table_that_I_want_to_import, on_delete=models.CASCADE, related_name="some_name", 
default=”default_value”) . 

For the many-to-many relationship between watchlists and URLs, I will need to use the ManyToManyField(). Since a user could 
have an empty watchlist (if they decide to not to add anything to a wishlist), I will use the “blank=true” property of 
the ManyToManyField(). The syntax could be like the following: models.ManyToManyField(table_that_I_want_to_import, 
blank=True, related_name=’some_name’) . 

Upon further consideration, I'm not storing the listings' URLs anywhere. So, 
it's pointless to make a Many To Many relationship here: there's no table with stored listing URLs to begin with. A simple
CharField to store the URLs will suffice.

Only 1 user can have 1 watchlist, and only 1 watchlist can belong to a single user. So, I need to use a foreign key
for the users, NOT a Many to Many relationship.

The column that contains the product's ID needs to be a Many To Many relationship since a single watchlist can have 
multiple products, and a single product can be added to multiple watchlists from multiple users. And Many To Many 
fields don't need a "on_delete" property.
"""
class Watchlists(models.Model):
    product_url = models.CharField(max_length=2048, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist_from_user", default=0)
    product_id = models.ManyToManyField(Listings, blank=True, related_name="ID_from_product", default=0)

""" Now, I need to add the “Category” input, which I will make as a dropdown menu. I need to look up on w3schools how to make 
this. In fact, I also have to look up how to make a dropdown input using Django forms.

The best way to do this would be to, first, create a “Categories” model, so that I can create a table for the categories. Then, 
I should add some entries (be it via the Python shell, or by executing SQL statements directly on the CMD on the database.) 
The entries could be like “Fashion”, “Toys”, etc. So, to do this, I should go back to the models.py file, and I should create a
model called “Categories”. For the time being, it will only have one field: the name of the category.

Since I assigned a limit of 64 characters to the “category” field on the “Listings” model, and I really don’t think that I will 
create a category with more than 64 characters, I will make the only field that the “Categories” model will have to also have a 
limit of 64 characters.

To fix the item names on the dropdown menu (so that it doesn’t display “category object(1/2/3/4)”), I needed to 
add a “__str__” snippet on the class that contains the Categories model, as Brian explained during the lecture.

"""
class Categories(models.Model):
    category = models.CharField(max_length=64, default='None')

    # This will change the dropdown menu items from "category object (1/2)" to the actual category name
    def __str__(self):
        return f"{self.category}"

    class Meta:
        verbose_name_plural = "Categories"