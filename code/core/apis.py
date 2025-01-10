from ninja import NinjaAPI, UploadedFile, File, Query, Router
from ninja_simple_jwt.auth.views.api  import mobile_auth_router
from ninja_simple_jwt.auth.ninja_auth import HttpJwtAuth
from typing import List

from core.schema import RegisterSchema, ProfileOutSchema
from core.schema import RestaurantOutSchema, RestaurantInSchema, MenuOutSchema, MenuInSchema
from core.schema import RestaurantFilterSchema, ProfileInSchema, UpdatePasswordSchema
from core.schema import ReviewOutSchema, ReviewInSchema, BookmarkInSchema, BookmarkOutSchema, RatingMenuOutSchema, RatingMenuInSchema

from core.models import User, Restaurant, Menu, Review, Bookmark, RatingMenu

ninja = NinjaAPI()
api = Router()
ninja.add_router('/auth/', mobile_auth_router)
ninja.add_router('/', api)
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
    resto = Restaurant.objects.get(id=resto_id)
    resto.image.save(image.name, image)
    return resto

@api.get('/resto/{resto_id}', response={200: RestaurantOutSchema}, auth=apiuth)
def get_single_resto(request, resto_id: int):
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

@api.get('/resto/{resto_id}/review', response={200: List[ReviewOutSchema]}, auth=apiuth)
def get_review(request, resto_id: int):
    resto = Restaurant.objects.get(id=resto_id)
    review = Review.objects.filter(restaurant=resto)
    return review

@api.post('/resto/{resto_id}/review', response={200: ReviewOutSchema}, auth=apiuth)
def create_review(request, resto_id: int, payload: ReviewInSchema):
    user = User.objects.get(id=request.user.id)
    resto = Restaurant.objects.get(id=resto_id)
    reviews = Review.objects.create(
        restaurant=resto,
        user=user,
        rating=payload.rating,
        comment=payload.comment)
    return reviews


@api.get('/review/{review_id}', response={200: ReviewOutSchema}, auth=apiuth)
def get_review(request, review_id: int):
    review = Review.objects.get(id=review_id)
    return review


@api.delete('/review/{review_id}', response={204: None, 403: dict}, auth=apiuth)
def delete_review(request, review_id: int):
    user = User.objects.get(id=request.user.id)
    review = Review.objects.get(id=review_id)
    if review.user != user:
        return 403, {'message': 'Hanya pemilik yang bisa menghapus review'}
    review.delete()

    return 204, None

@api.put('/review/{review_id}', response={200: ReviewOutSchema}, auth=apiuth)
def update_review(request, review_id: int, payload: ReviewInSchema):
    user = User.objects.get(id=request.user.id)
    review = Review.objects.get(id=review_id)
    if review.user != user:
        return 403
    review.rating = payload.rating
    review.comment = payload.comment
    review.save()
    return review

@api.get('/bookmark', response={200: List[BookmarkOutSchema]}, auth=apiuth)
def get_bookmark(request):
    user = User.objects.get(id=request.user.id)
    bookmark = Bookmark.objects.filter(user=user)
    return bookmark

@api.post('/bookmark', response={200: BookmarkOutSchema}, auth=apiuth)
def create_bookmark(request, payload: BookmarkInSchema):
    user = User.objects.get(id=request.user.id)
    bookmark = Bookmark.objects.create(
        user=user,
        restaurant=payload.restaurant)
    return bookmark
    
@api.delete('/bookmark/{bookmark_id}', response={204: None, 403: dict}, auth=apiuth)
def delete_bookmark(request, bookmark_id: int):
    user = User.objects.get(id=request.user.id)
    bookmark = Bookmark.objects.get(id=bookmark_id)
    if bookmark.user != user:
        return 403, {'message': 'Hanya pemilik yang bisa menghapus bookmark'}
    
@api.get('/menu/{menu_id}/rating', response={200: List[RatingMenuOutSchema]}, auth=apiuth)
def get_rating_menu(request, menu_id: int):
    menu = Menu.objects.get(id=menu_id)
    rating = RatingMenu.objects.filter(menu=menu)
    return rating

@api.post('/menu/{menu_id}/rating', response={200: RatingMenuOutSchema}, auth=apiuth)
def create_rating_menu(request, menu_id: int, payload: RatingMenuInSchema):
    user = User.objects.get(id=request.user.id)
    menu = Menu.objects.get(id=menu_id)
    rating = RatingMenu.objects.create(
        menu=menu, user=user, rating=payload.rating)
    
    return rating

@api.put('/rating/{rating_id}', response={200: RatingMenuOutSchema, 403: dict}, auth=apiuth)
def update_rating_menu(request, rating_id: int, payload: RatingMenuInSchema):
    user = User.objects.get(id=request.user.id)
    rating = RatingMenu.objects.get(id=rating_id)
    if rating.user != user:
        return 403, {'message': 'Hanya pemilik yang bisa mengubah rating'}
    return 200, rating

