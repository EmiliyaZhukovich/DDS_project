from django.urls import path
from .views import (
    MovementListView,
    MovementCreateView,
    MovementUpdateView,
    MovementDeleteView,
    categories_by_type,
    subcategories_by_category,
)

urlpatterns = [
    path('', MovementListView.as_view(), name='movement_list'),
    path("create/", MovementCreateView.as_view(), name="movement_create"),
    path("<int:pk>/edit/", MovementUpdateView.as_view(), name="movement_edit"),
    path("<int:pk>/delete/", MovementDeleteView.as_view(), name="movement_delete"),
    path("api/categories/", categories_by_type, name="api_categories_by_type"),
    path("api/subcategories/", subcategories_by_category, name="api_subcategories_by_category"),
]

