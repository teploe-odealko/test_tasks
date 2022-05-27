from django.urls import include, path
from menu.views import FoodList

urlpatterns = [
    path('foods/', FoodList.as_view()),
]
