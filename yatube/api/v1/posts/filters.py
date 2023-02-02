import django_filters
from posts import models


# CHOICES =[
#         ["name", "по алфавиту"],
#         ["price", "дешевые сверху"],
#         ["-price", "дорогие сверху"]
# ]
# ordering = django_filters.OrderingFilter(choices=CHOICES, required=True, empty_label=None,)


class Group(django_filters.FilterSet):
    # title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    # description = django_filters.CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = models.Group
        fields = '__all__'
        # fields = ('slug',)


class Post(django_filters.FilterSet):
    id = django_filters.NumberFilter(field_name='id')
    author = django_filters.CharFilter(field_name='author__username', lookup_expr='icontains')
    group = django_filters.CharFilter(field_name='group__slug', lookup_expr='icontains')

    class Meta:
        model = models.Post
        exclude = ('image',)


class Comment(django_filters.FilterSet):
    author = django_filters.CharFilter(field_name='author__username',
                                       lookup_expr='icontains')
    id = django_filters.NumberFilter(field_name='post__id')

    class Meta:
        model = models.Comment
        fields = ('author', )
