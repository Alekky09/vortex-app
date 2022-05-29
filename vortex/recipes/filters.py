from rest_framework import filters
from django.db.models import Count, Max, Min


class MinMaxFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if 'minmax_filter' in request.query_params:
            filter = request.query_params.get('minmax_filter')
            queryset = queryset.annotate(Count('ingredients'))
            if filter == 'max':
                max_count = queryset.aggregate(Max('ingredients__count'))['ingredients__count__max']
                return queryset.filter(ingredients__count=max_count)
            elif filter == 'min':
                min_count = queryset.aggregate(Min('ingredients__count'))['ingredients__count__min']
                return queryset.filter(ingredients__count=min_count)
        return queryset
