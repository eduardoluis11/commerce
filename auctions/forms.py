""" This will allow me to generate HTML forms by using Django (source:
https://docs.djangoproject.com/en/4.0/topics/forms/) """
from django import forms

""" After reading the Django documentation on how to create Django forms, I decided to create the forms using 
Django’s libraries and tools instead of manually writing HTML forms in layouts.html. So, to create the forms, I 
decided to create a new file called forms.py. There, I will import the needed libraries to create forms. Then, from 
views.py and layout.html, I will call the forms from forms.py. I will put the forms.py file in the “auctions” folder, 
so that it’s located in the same directory as the views.py file.

2.b) They should be able to specify a title for the listing, a text-based description, and what the starting bid should 
be. 

I will use the forms.py file that I created to generate the forms that I will use to get the title, description, and 
the starting bid of the new listing in the “create listing” page.

The basic syntax that I will need to generate a Django form in the forms.py file will be the following: 
“class NameOfTheForm(forms.Form):” (source: https://docs.djangoproject.com/en/4.0/topics/forms/ . ) The code that 
should go after that is pretty much exactly the same as the Field() functions that I used in the models.py file 
(for instance, “CharField()”). The only difference is that, instead of typing “models.CharField()”, I’ll have to 
type “forms.CharField()”.

I want the description input of the form that will let the user create a listing to be a <textarea> (so that they have 
a large rectangle for them to type the description.) To do that using Django forms, I need to add a widget, which is 
an extra parameter that I need to add to the Field() function that will generate the form. The widget should have the 
following syntax: “CharField(widget=forms.Textarea)” (source: https://docs.djangoproject.com/en/4.0/topics/forms/ .)

Since all of the inputs that I’m creating will get the text that I will insert into the database, I will apply the 
exact same restrictions that I gave to those specific fields in the models.py file.
"""
class CreateListingForm(forms.Form):
    listing_title = forms.CharField(max_length=128)
    starting_bid = forms.DecimalField(max_digits=12, decimal_places=2)
    description = forms.CharField(max_length=4500, widget=forms.Textarea)