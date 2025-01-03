from ninja import NinjaAPI, UploadedFile, File, Query
from ninja_simple_jwt.auth.views.api  import mobile_auth_router
from ninja_simple_jwt.auth.ninja_auth import HttpJwtAuth
from typing import List

from core.schema import RegisterSchema, ProfileOutSchema
from core.schema import RestaurantOutSchema, RestaurantInSchema, MenuOutSchema, MenuInSchema
from core.schema import RestaurantFilterSchema, ProfileInSchema, UpdatePasswordSchema

from core.models import User, Restaurant, Menu, Review, Bookmark

api = NinjaAPI()
api.add_router('/auth/', mobile_auth_router)
apiuth = HttpJwtAuth()

@api.post('/register', response={200: ProfileOutSchema})
def register(request, payload: RegisterSchema):
    user = User.objects.create_user(
        username=payload.username,
        password=payload.password,
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name
    )
    return user

@api.get('/resto', response={200: List[RestaurantOutSchema]}, auth=apiuth)
def get_resto(request, filters: RestaurantFilterSchema=Query(...)):
    resto = Restaurant.objects.all()
    resto = filters.filter(resto)
    return resto

@api.post('/resto', response={201: RestaurantOutSchema}, auth=apiuth)
def create_resto(request, payload: RestaurantInSchema):
    user = User.objects.get(id=request.user.id)
    resto = Restaurant.objects.create(
        name=payload.name, owner=user,
        description=payload.description, address=payload.address,
        website=payload.website, phone=payload.phone,
        lattitude=payload.lattitude, longitude=payload.longitude)
    return resto

@api.post('/resto/{resto_id}/image', auth=apiuth, response={200: RestaurantOutSchema})
def upload_resto_image(request, resto_id:int, image: UploadedFile = File(...)):
    # data = image.read()
    resto = Restaurant.objects.get(id=resto_id)
    resto.image.save(image.name, image)
    return resto

@api.get('/resto/{resto_id}', response={200: RestaurantOutSchema}, auth=apiuth)
def get_resto(request, resto_id: int):
    resto = Restaurant.objects.get(id=resto_id)
    return resto

@api.put('/resto/{resto_id}', response={200: RestaurantOutSchema}, auth=apiuth)
def update_resto(request, resto_id: int, payload: RestaurantInSchema):
    resto = Restaurant.objects.get(id=resto_id)
    resto.name = payload.name
    resto.description = payload.description
    resto.address = payload.address
    resto.website = payload.website
    resto.lattitude = payload.lattitude
    resto.longitude = payload.longitude
    resto.save()
    return resto

@api.get('/profile', response={200: ProfileOutSchema}, auth=apiuth)
def get_profile(request):
    user = User.objects.get(id=request.user.id)
    return user

@api.put('/profile', response={200: ProfileOutSchema}, auth=apiuth)
def update_profile(request, payload: ProfileInSchema):
    user = User.objects.get(id=request.user.id)
    user.email = payload.email
    user.first_name = payload.first_name
    user.last_name = payload.last_name

    user.save()
    return user

@api.put('/profile/password', response={200: dict}, auth=apiuth)
def update_password(request, payload: UpdatePasswordSchema):
    user = User.objects.get(id=request.user.id)
    if not user.check_password(payload.old_password):
        raise ValueError('Password lama tidak sesuai')
    user.set_password(payload.new_password)
    user.save()
    return {'message': 'Password berhasil diubah'}

@api.get('/resto/{resto_id}/menu', response={200: List[MenuOutSchema]}, auth=apiuth)
def get_menu(request, resto_id: int):
    resto = Restaurant.objects.get(id=resto_id)
    menu = Menu.objects.filter(restaurant=resto)
    return menu

@api.post('/resto/{resto_id}/menu', response={201: MenuOutSchema, 403: dict}, auth=apiuth)
def create_menu(request, resto_id: int, payload: MenuInSchema):
    user = User.objects.get(id=request.user.id)
    resto = Restaurant.objects.get(id=resto_id)
    if resto.owner != user:
        return 403, {'message': 'Hanya pemilik yang bisa menambahkan menu'}
    menu = Menu.objects.create(
        restaurant=resto,
        name=payload.name,
        description=payload.description,
        price=payload.price)
    return 201, menu

@api.post('/menu/{menu_id}/image', auth=apiuth, response={200: MenuOutSchema})
def upload_menu_image(request, menu_id:int, image: UploadedFile = File(...)):
    menu = Menu.objects.get(id=menu_id)
    menu.image.save(image.name, image)
    return menu

@api.get('/menu/{menu_id}', response={200: MenuOutSchema}, auth=apiuth)
def get_menu(request, menu_id: int):
    menu = Menu.objects.get(id=menu_id)
    return menu

@api.delete('/menu/{menu_id}', response={204: None, 403: dict}, auth=apiuth)
def delete_menu(request, menu_id: int):
    user = User.objects.get(id=request.user.id)
    menu = Menu.objects.get(id=menu_id)
    if menu.restaurant.owner != user:
        return 403, {'message': 'Hanya pemilik yang bisa menghapus menu'}
    menu.delete()
    return 204, None