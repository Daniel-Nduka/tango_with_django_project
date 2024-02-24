from django.shortcuts import render

from django.http import HttpResponse

#Import category model
from rango.models import Category

#import Page model
from rango.models import Page

#import the catgery form
from rango.forms import CategoryForm
from django.shortcuts import redirect

#import the page form
from rango.forms import PageForm
from django.urls import reverse

#import the userForm
from rango.forms import UserForm, UserProfileForm

#import authentication
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

#import date_time
from datetime import datetime

def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
      # Get the top five most viewed pages
    page_list = Page.objects.order_by('-views')[:5]

    #pages = Page.objects.order_by('-likes')[:5]
    
    context_dict = {}
    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage matches to {{ boldmessage }} in the template!
    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
    context_dict['categories'] = category_list

    context_dict['pages'] = page_list
    
    visitor_cookie_handler(request)


    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    request.session.set_test_cookie()
    response = render(request, 'rango/index.html', context=context_dict)
    visitor_cookie_handler(request)

    return response


def about(request):
    context_dict = {'boldmessage': 'This tutorial has been put together by Nduka ofoeyeno'}
    if request.session.test_cookie_worked():
        visitor_cookie_handler(request)
        context_dict['visits'] = request.session['visits']
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()
    return render(request, 'rango/about.html', context=context_dict)

def show_category(request, category_name_slug):
    # Create a context dictionary which we can pass
    # to the template rendering engine.
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve all of the associated pages.
        # The filter() will return a list of page objects or an empty list.
        pages = Page.objects.filter(category=category)

        context_dict['pages']= pages

        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything -
        # the template will display the "no category" message for us.
        context_dict['category'] = None
        context_dict['pages'] = None
    return render(request, 'rango/category.html', context=context_dict)

@login_required
def add_category(request):
    form = CategoryForm()

    #A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        #Have we been provided with a vialid form?
        if form.is_valid():
            #Save the new category to the database
            form.save(commit=True)
            #Now that the category is saved we could confirkm this
            #For now, just redirect the user back to the indec view
            return redirect('/rango/')
        else:
            #the supplied form contained errors, print them to terminal
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    
    # You cannot add a page to a Category that does not exist...
    if category is None:
        return redirect('/rango/')
    
    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return redirect(reverse('rango:show_category',
                                        kwargs={'category_name_slug':
                                                category_name_slug}))
        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)




@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))

                 
    last_visit_cookie = get_server_side_cookie(request, 'last_visit',
                                              str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')
    # If it's been more than a day since the last visit...
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # Update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else:
        # Set the last visit cookie
        request.session['last_visit'] = last_visit_cookie
    # Update/set the visits cookie
    request.session['visits'] = visits
                             
    
