from ninja import Schema, ModelSchema, FilterSchema
from datetime import datetime
from typing import Optional, List
from django.db.models import Q

from pydantic  import field_validator, Field

from core.models import Restaurant, Menu, Review, Bookmark, RatingMenu

class RegisterSchema(Schema):
    username: str
    password: str
    confirmation: str
    email: str
    first_name: str
    last_name: str

    @field_validator('password')
    def validate_password(cls, value, form_data):
        if len(value) < 8:
            raise ValueError('Password harus lebih dari 8 karakter')
        if 'password' in form_data.data and value != form_data.data['confirmation']:
            raise ValueError('Password dan konfirmasi password harus sama')
        return value
    
class RestaurantOutSchema(ModelSchema):
    class Config:
        model = Restaurant
        model_fields = ['id', 'name', 'owner', 'description', 'address', 
                        'phone', 'website', 'lattitude', 'longitude', 
                        'image', 'created_at', 'updated_at'] 
        
class RestaurantFilterSchema(FilterSchema):
    search: Optional[str] = Field(None, q=['name__icontains', 'description__icontains'])    
        
class RestaurantInSchema(ModelSchema):
    class Config:
        model = Restaurant
        model_fields = ['name', 'description', 'address',
                        'phone', 'website', 'lattitude', 'longitude']

class ProfileOutSchema(Schema):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    restaurant: Optional[RestaurantOutSchema] = None

    @staticmethod
    def resolve_restaurant(obj):
        resto = Restaurant.objects.filter(owner=obj.id).first()
        if resto is None:
            return None
        return resto

class ProfileInSchema(Schema):
    email: str
    first_name: str
    last_name: str

class UpdatePasswordSchema(Schema):
    old_password: str
    new_password: str
    confirmation: str

    @field_validator('new_password')
    def validate_password(cls, value, form_data):
        if len(value) < 8:
            raise ValueError('Password harus lebih dari 8 karakter')
        if 'password' in form_data.data and value != form_data.data['confirmation']:
            raise ValueError('Password dan konfirmasi password harus sama')
        return value
        
class MenuOutSchema(ModelSchema):
    class Config:
        model = Menu
        model_fields = ['id', 'restaurant', 'name', 'description', 'price', 'image', 'created_at', 'updated_at']

class MenuInSchema(ModelSchema):
    class Config:
        model = Menu
        model_fields = ['restaurant', 'name', 'description', 'price']

class ReviewOutSchema(Schema):
    id: int
    restaurant: RestaurantOutSchema
    user: ProfileOutSchema
    rating: int
    comment: str
    created_at: datetime
    updated_at: datetime
    

class ReviewInSchema(ModelSchema):
    class Config:
        model = Review
        model_fields = ['restaurant', 'user', 'rating', 'comment']

class BookmarkOutSchema(ModelSchema):
    class Config:
        model = Bookmark
        model_fields = ['id', 'user', 'restaurant']

class BookmarkInSchema(ModelSchema):
    class Config:
        model = Bookmark
        model_fields = ['user', 'restaurant']

class RatingMenuOutSchema(Schema):
    id: int
    user: ProfileOutSchema
    menu: MenuOutSchema
    rating: int
    created_at: datetime
    updated_at: datetime

class RatingMenuInSchema(ModelSchema):
    class Config:
        model = RatingMenu
        model_fields = ['rating']