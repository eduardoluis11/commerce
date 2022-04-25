from django.urls import path

from . import views

""" I added a path called "create", which will redirect the user to the "/create" page so that they can create a new
listing.

 I need to create a page specific for each listing. I will use the ID of each listing to differentiate the URL from 
 each listing page. To do that, I will need to insert the ID of the currently clicked listing into a string from the 
 views.py field (if I’m not mistaken), and then insert it into the “<str” keyword in urls.py.
 
 The 'inactive' link will send the users to a list of all the closed auctions.
"""
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listing/<str:listing_id>", views.display_listing, name="display_listing"),
    path("inactive", views.inactive_listings, name="inactive_listings"),

]
