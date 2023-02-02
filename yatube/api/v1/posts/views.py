from rest_framework.generics import RetrieveAPIView, GenericAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from posts import models
from . import serializers, filters
from .permissions import UserPermissions


class BaseViewSet(ModelViewSet):
    permission_classes = (UserPermissions,)
    authentication_classes = (SessionAuthentication, TokenAuthentication)


class PostViewSet(BaseViewSet):
    queryset = models.Post.objects.select_related('author', 'group')
    filterset_class = filters.Post

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'list':
            return serializers.Post
        if self.action == 'retrieve':
            return serializers.PostDetail
        if self.action in ['create', 'update', 'put']:
            return serializers.AddPost
        return serializers.Post

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()


class GroupViewSet(ReadOnlyModelViewSet):
    permission_classes = (UserPermissions,)
    queryset = models.Group.objects.all()
    serializer_class = serializers.Group
    filterset_class = filters.Group
    lookup_field = 'slug'


class ProfileDetail(RetrieveAPIView):
    permission_classes = (UserPermissions, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    queryset = models.User.objects.all()
    serializer_class = serializers.User
    lookup_field = 'username'


class CommentViewSet(BaseViewSet):
    queryset = models.Comment.objects.all()
    serializer_class = serializers.Comment
    filter_class = filters.Comment


class FollowViewSet(GenericAPIView):
    queryset = models.Follow.objects.all()

    # def get_queryset(self, **kwargs):
    #     slug = self.kwargs['pk']
    #     group = get_object_or_404(Group, slug)
    #     queryset = group.post_set.all().select_related('author')
    #     # queryset = models.Post.objects.select_related('author', 'group').filter(group=id)
    #     return queryset


    # @action(detail=True, methods=['post'], name='Create post')
    # def perform_create(self, serializer, *args, **kwargs):
    #     serializer.save(author=self.request.user)
    # # или?
    #     serializer.validated_data['author'] = self.request.user
    #     serializer.save()


    # def get_queryset(self, *args, **kwargs):
    #     group = get_object_or_404(Group, slug=args)
    #     queryset = group.post_set.all().select_related('author')
    #     return queryset



# class Index(ListAPIView):
#     queryset = models.Post.objects.select_related('author', 'group')
#     serializer_class = serializers.Post
#     filters_class = filters.Post

    # def list(self, request, *args, **kwargs):
    #     serializer = serializers.PostSearch(data=request.query_params)
    #     serializer.is_valid(raise_exception=True)
    #     return super().list(request, *args, **kwargs)
