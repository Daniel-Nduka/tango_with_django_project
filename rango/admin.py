from django.contrib import admin

# Register your models here.
from rango.models import Category, Page

# Add in this class to customise the Admin Interface

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}
# Update the registration to include this customised interface
admin.site.register(Category, CategoryAdmin)

class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')

# Register the Page model with the custom admin class
admin.site.register(Page, PageAdmin)

from rango.models import UserProfile
admin.site.register(UserProfile)
