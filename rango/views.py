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
from django.utils.decorators import method_decorator
#import date_time
from datetime import datetime

#import bing search
from rango.bing_search import run_query

from django.views import View

from django.contrib.auth.models import User
from rango.models import UserProfile

class IndexView(View):

    def get(self, request):
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


class AboutView(View):
    def get(self, request):
        context_dict = {'boldmessage': 'This tutorial has been put together by Nduka ofoeyeno'}
        visitor_cookie_handler(request)
        context_dict['visits'] = request.session['visits']
        
        request.session.delete_test_cookie()
        return render(request, 'rango/about.html', context=context_dict)

class ShowCategoryView(View):

    def create_context_dict(self, category_name_slug):
        context_dict = {}
        try:
            category = Category.objects.get(slug=category_name_slug)
            pages = Page.objects.filter(category=category).order_by('-views')
            context_dict['pages'] = pages
            context_dict['category'] = category
        except Category.DoesNotExist:
            context_dict['category'] = None
            context_dict['pages'] = None
        return context_dict

    def get(self, request, category_name_slug):
        context_dict = self.create_context_dict(category_name_slug)
        return render(request, 'rango/category.html', context_dict)

    def post(self, request, category_name_slug):
        context_dict = self.create_context_dict(category_name_slug)
        query = request.POST['query'].strip()
        if query:
            context_dict['result_list'] = run_query(query)
            # End new search functionality code.
        return render(request, 'rango/category.html', context_dict)


class AddCategoryView(View):

    @method_decorator(login_required)
    def get(self, request):
        form = CategoryForm()
        return render(request, 'rango/add_category.html', {'form': form})

        #A HTTP POST?
    @method_decorator(login_required)
    def post(self, request):
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            #Now that the category is saved we could confirm this
            #For now, just redirect the user back to the indec view
            return redirect('/rango/')
        else:
            #the supplied form contained errors, print them to terminal
            print(form.errors)

        return render(request, 'rango/add_category.html', {'form': form})


class AddPageView(View):
    @method_decorator(login_required)
    def get(self, request, category_name_slug):
        try:
            category = Category.objects.get(slug=category_name_slug)
        except Category.DoesNotExist:
            category = None
            # You cannot add a page to a Category that does not exist...
            if category is None:
                return redirect('/rango/')
        context_dict = {'category': category} 

        return render(request, 'rango/add_page.html', context=context_dict)
    @method_decorator(login_required)
    def post(self, request, category_name_slug):
        
        form = PageForm(request.POST)
        context_dict = {'form': form}


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
            return render(request, 'rango/add_page.html', context=context_dict)


class RestrictedView(View):
    @method_decorator(login_required)
    def get(self, request):
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
'''
def search(request):
    result_list = []
    if request.method =='POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
    return render(request, 'rango/search.html', {'result_list': result_list})
'''
class GotoView(View):
    def get(self, request):
        page_id = None
    #if request.method =='GET':
        page_id = request.GET.get('page_id')
        try:
            selected_page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
           # we use reverse to dynamically generate a url from a view 
            reverse_url = reverse('rango:index')
            #we use ridrect to direct the user to that url
            return redirect(reverse_url)

        selected_page.views = selected_page.views + 1
        selected_page.save()
        return redirect(selected_page.url)


class RegisterProfileView(View):
    def get(self, request):
        form = UserProfileForm()
        context_dict = {'form': form}
        return render(request, 'rango/profile_registration.html', context_dict)
    def post(self, request):
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)
            context_dict = {'form': form}
        return render(request, 'rango/profile_registration.html', context_dict)

class ProfileView(View):
    def get_user_details(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        user_profile = UserProfile.objects.get_or_create(user=user)[0]
        form = UserProfileForm({'website': user_profile.website,
                                'picture': user_profile.picture})
        return (user, user_profile, form)

    @method_decorator(login_required)
    def get(self, request, username):
        try:
            (user, user_profile, form)= self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))
        context_dict = {'user_profile': user_profile,
                        'selected_user': user,
                        'form': form}

        return render(request, 'rango/profile.html', context_dict)

    @method_decorator(login_required)
    def post(self, request, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)

        except TypeError:
            return redirect(reverse('rango:index'))

        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save(commit=True)
            return redirect('rango:profile', user.username)
        else:
            print(form.errors)

        context_dict = {'user_profile': user_profile,
                        'selected_user': user,
                        'form': form}

        return render(request, 'rango/profile.html', context_dict)

class ListProfilesView(View):
    @method_decorator(login_required)
    def get(self, request):
        profiles = UserProfile.objects.all()

        return render(request,
                      'rango/list_profiles.html',
                      {'userprofile_list': profiles})


    
                             
    
