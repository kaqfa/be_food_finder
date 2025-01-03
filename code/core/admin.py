from django.contrib import admin
from core.models import Restaurant, Menu, Review, User


class MenuInline(admin.StackedInline):
    model = Menu
    extra = 1

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'address', 'created_at', 'updated_at')
    fields = ('name', 'owner', 'description', 'address', 'phone', 'website', 'lattitude', 'longitude', 'image')
    search_fields = ('name', 'owner', 'address', 'phone')
    ordering = ('-created_at',)
    inlines = [MenuInline]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'user', 'rating', 'comment', 'created_at')
    fields = ('restaurant', 'user', 'rating', 'comment')
    search_fields = ('restaurant', 'user', 'rating', 'comment')
    ordering = ('-created_at',)