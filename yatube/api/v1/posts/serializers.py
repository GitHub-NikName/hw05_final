from rest_framework import serializers
from posts import models


class User(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name')
    follower_count = serializers.SerializerMethodField()

    class Meta:
        model = models.User
        fields = ('full_name', 'username', 'first_name', 'last_name', 'follower_count')
        # list_serializer_class = 'Post'
        # read_only_fields = [f.name for f in model._meta.get_fields()]

    @classmethod
    def get_follower_count(cls, obj):
        return obj.following.count()


class Group(serializers.ModelSerializer):
    class Meta:
        model = models.Group
        exclude = ('id', )


class Post(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    full_name = serializers.ReadOnlyField(source='author.get_full_name')
    group = serializers.ReadOnlyField(source='group.slug', read_only=True)

    class Meta:
        model = models.Post
        fields = '__all__'  # ('author', 'group', 'id')
        read_only_fields = ('author', 'full_name', 'group_slug')
        # depth = 1


class AddPost(serializers.ModelSerializer):
    """Сериализация добавления статьи"""

    class Meta:
        model = models.Post
        fields = ('text', 'group', 'image')

    # def get_display(obj: models.Post) -> str:
    #     return f'{obj.author}. {obj.group}'


class Comment(serializers.ModelSerializer):
    """Сериализация комментариев"""
    author = serializers.SlugRelatedField(read_only=True, slug_field='username')
    # text = serializers.SerializerMethodField()

    class Meta:
        model = models.Comment
        fields = ('author', 'text')


class PostDetail(Post):
    # group = serializers.SlugRelatedField(read_only=True, slug_field='slug')
    comments = Comment(many=True, read_only=True)
    count_posts_author = serializers.SerializerMethodField()

    class Meta:
        model = models.Post
        # fields = ('author', 'created', 'text', 'image', 'group', 'comments', 'posts_author_count')
        fields = '__all__'

    @classmethod
    def get_count_posts_author(cls, obj):
        return obj.author.posts.count()


# class PostSearch(serializers.Serializer):
#     author = serializers.CharField(label='Автор', required=True)
#
#     def validate_author(self, value):
#         if not models.Post.objects.filter(author__=value):
#             raise serializers.ValidationError(f'Нет меток содержащих "{value}"')
#         return value

    # def validate(self, attrs):
    #
    #     return attrs
