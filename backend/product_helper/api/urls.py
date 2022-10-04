from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomUserView, TagListRetrieveViewSet, create_token, delete_token

app_name = 'api'

router_v1 = DefaultRouter()

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
urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/token/logout/', delete_token, name='logout'),
    path('auth/token/login/', create_token, name='login'),
]
