from django.urls import path

from . import views

""" Now, I need to create the Admin panel. To do that, I need to review Brian’s lecture. I will need to add some 
code to add a library that will let me create the admin panel.

I don’t have the default URL for “admin” in urls.py. I will have to add it. I don’t even have the “admin” library 
imported in the urls.py file. I will have to add both things.

"""
# This imports the library to let me use the Admin panel (source: Brian's lecture for this assignment)
from django.contrib import admin


""" I added a path called "create", which will redirect the user to the "/create" page so that they can create a new
listing.

 I need to create a page specific for each listing. I will use the ID of each listing to differentiate the URL from 
 each listing page. To do that, I will need to insert the ID of the currently clicked listing into a string from the 
 views.py field (if I’m not mistaken), and then insert it into the “<str” keyword in urls.py.
 
 The 'inactive' link will send the users to a list of all the closed auctions.
 
 The 'watchlist' link will send the users to their watchlist
 
 The 'admin' link will send me to the admin panel (source: Brian's lecture for this assignment.)
"""
urlpatterns = [
    path("admin", admin.site.urls),
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listing/<str:listing_id>", views.display_listing, name="display_listing"),
    path("inactive", views.inactive_listings, name="inactive_listings"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category_id>", views.category_listings, name="category_listings"),

]