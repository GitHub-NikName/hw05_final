from django.urls import path
from rest_framework_swagger.views import get_swagger_view
from rest_framework.routers import DefaultRouter

from api.v1.posts import views

schema_view = get_swagger_view(title='API')

urlpatterns = [
    path('', schema_view),
    path(
        r'profile/<str:username>/',
        views.ProfileDetail.as_view(),
        name="profile"
    ),
    # path('create/', include('posts.urls')),
]

router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename="post")
router.register(r'group', views.GroupViewSet, basename="group")
router.register(r'comments', views.CommentViewSet, basename="comments")
urlpatterns += router.urls
