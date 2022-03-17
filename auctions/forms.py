""" This will allow me to generate HTML forms by using Django (source:
https://docs.djangoproject.com/en/4.0/topics/forms/) """
from django import forms

# This will import the Listings,Categories, and all the other tables from the models.py file
from .models import Listings, Categories, Bids, Comments, Watchlists

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

2.c) Users should also optionally be able to provide a URL for an image for the listing and/or a category (e.g. Fashion, Toys, Electronics, Home, etc.)
Answer:
The images won’t be stored locally within the web app. Instead, they will be taken from a CDN, or just any URL with an 
image. 

I will make sure that I have created a model for both the URL and category inputs. After checking my models, I have 
indeed created them.

Next, I need to create the inputs that will let the user type the picture’s URL, and choose its category. I don’t want 
the user to type a category. The “category” section should be an option from a dropdown menu. I will look for the <select> tag (or something like that) in W3Schools.

I want to use copyright free pictures. I will look them up in Pixabay, Pexels, and Unsplash, since they are 
royalty-free images. 
First, I’ll create the input for the URL. Let me see in the Django documentation for the Django forms if there’s a 
“Field” type for URLs. Although I think it would be enough using the “CharField” input type. After checking the models, 
I see that I already added a “CharField” type for the database entry that will store the URLs. So, I will use that 
exact same data type, and I will assign the exact same limits as in “picture_url” from the models.

However, remember that the URL should be OPTIONAL. And, by default, Django dorms make every field to be “required”. I 
will check how to remove the “required” tag from the inputs generated by Django forms. 
To remove the “required” attribute from the “URL” input, it seems that I need to use 
“CharField(use_required_attribute=False)” in views.py (source: anupsabraham’s reply from 
https://stackoverflow.com/questions/54587726/how-to-remove-required-attribute-from-django-form .) However, this seems 
to turn EVERY attribute to lose their “required” status. I DON’T want that. I only want the URL and the Category fields 
to be optional.

But, regardless of whether the picture is required or not, the picture is not being rendered. I need to check out why 
this is happening.

It’s storing the URL properly. The problem is that the image isn’t being rendered, and I don’t know why.

I figured out what the problem was: I was storing the URL with the page that had the image AND some other content. 
I wasn’t storing the URL of only the picture. I needed the URL that has only the image, not any other content nor 
text (i.e: a URL with a “.jpg” o “.gif” ending.)

I think I found what I was looking for, that is, I found out how to make a specific field from a form to not to have 
the “required” field. I need to go back to may models.py file, and, on the class with the forms, I need to create an 
“init” function that will declare that a specific field will not have the “required” atttribute  (source: madzohan’s 
reply from     https://stackoverflow.com/questions/16205908/django-modelform-not-required-field .)
	
The real solution was to put “required=False”, inside of the “forms.CharField()” parentheses for the field that stores 
the picture URL (source: Akshar Raaj’s reply from 
https://stackoverflow.com/questions/16205908/django-modelform-not-required-field .)

I already created the “Categories” model, and I added four entries to it via SQL statements (such as “Fashion” and “Gaming”).

Now, I will go to my forms.py file, and I will add the optional “category” field. To make it into a <select> input, that is, 
to make it into a dropdown menu, I will use the “forms.ModelChoiceField()” field type. Then, to select all the categories 
from the Category table, I will use the following Query Set statement: “queryset=Categories.objects.all()”, where “Categories” 
is the model with the categories, which I’m importing from models.py (source: tread’s reply from 
https://stackoverflow.com/questions/48140291/how-to-create-a-custom-django-form-with-select-fields-from-different-models .) 
Finally, to make it optional, I will add “required=False” as an attribute.

BUG FIX: I was able to show the category names on both the dropdown list and on each entry of the database when submitting the 
form by replacing “Categories.objects.all()” by “Categories.objects.values_list(‘category’)”, so that, instead of grabbing the 
entire row for a specific entry of the “Categories” table, I’m only grabbing the name of the column (that is, instead of the ID
and the category name, I’m only grabbing the category name)  (source:
https://www.codegrepper.com/code-examples/python/django+query+select+specific+columns .)

However, it seems that I now have to clean the data, since I’m getting “ (‘Gaming’,) ” or “ (‘Category_name’,) ” as the category 
name. I need to remove the parentheses, the quotation marks, and the commas.

BUG FIX: By using the “__str__” snippet on the Categories model, and then reverting the MultipleChoiceField field on 
the form for the categories to “queryset: objects.all()”, I’m getting the name of the categories with the proper format.

"""
class CreateListingForm(forms.Form):
    listing_title = forms.CharField(max_length=128)
    starting_bid = forms.DecimalField(max_digits=12, decimal_places=2)
    description = forms.CharField(max_length=4500, widget=forms.Textarea)
    picture_url = forms.CharField(max_length=2048, required=False)
    category = forms.ModelChoiceField(queryset=Categories.objects.all(), required=False)