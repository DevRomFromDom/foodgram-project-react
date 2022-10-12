from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserView, FavoriteCreateDestroyView,
                    FollowListViewSet, FollowView, IngredientsListRetrieveView,
                    RecipesViewSet, ShoppingCartCreateDestroyView,
                    TagListRetrieveViewSet, create_token, delete_token)

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register(
    prefix='users/subscriptions',
    viewset=FollowListViewSet,
    basename='subscriptions'
)

router_v1.register(
    prefix='users',
    viewset=CustomUserView,
    basename='users'
)
router_v1.register(
    prefix='tags',
    viewset=TagListRetrieveViewSet,
    basename='tags'
)
router_v1.register(
    prefix='recipes',
    viewset=RecipesViewSet,
    basename='recipes'
)
router_v1.register(
    prefix='ingredients',
    viewset=IngredientsListRetrieveView,
    basename='ingredients'
)


urlpatterns = [
    path('api/recipes/download_shopping_cart/',
         ShoppingCartCreateDestroyView.as_view(),
         name='shopping_cart-txt'),
    path('api/auth/token/logout/', delete_token, name='logout'),
    path('api/auth/token/login/', create_token, name='login'),
    path('api/', include(router_v1.urls)),

    re_path(r'api/recipes/(?P<id>\d+)/favorite',
            FavoriteCreateDestroyView.as_view(),
            name='favorite'),

    re_path(r'api/recipes/(?P<id>\d+)/shopping_cart',
            ShoppingCartCreateDestroyView.as_view(),
            name='shopping_cart'),
    re_path(r'api/users/(?P<id>\d+)/subscribe',
            FollowView.as_view(),
            name='subscribe'),
]
