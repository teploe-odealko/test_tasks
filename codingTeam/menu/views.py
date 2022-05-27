from django.db.models import Prefetch, Count
from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

from menu.models import FoodCategory, Food
from menu.serializers import FoodListSerializer


class FoodList(ListAPIView):
    serializer_class = FoodListSerializer
    queryset = FoodCategory.objects\
        .prefetch_related(
            Prefetch(
                "food",
                queryset=Food.objects.filter(is_publish=True),
            ))\
        .prefetch_related('food__additional')\
        .annotate(food_count=Count('food')).filter(food_count__gt=0)
