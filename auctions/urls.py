from django.urls import path

from . import views

""" I added a path called "create", which will redirect the user to the "/create" page so that they can create a new
listing.
"""
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),

]
