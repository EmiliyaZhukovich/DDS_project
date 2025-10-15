from django.contrib import admin
from .models import Status, MovementType, Category, SubCategory, Movement

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(MovementType)
class MovementTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'movement_type')
    list_filter = ('movement_type',)
    search_fields = ('name',)

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "status",
        "movement_type",
        "category",
        "subcategory",
        "amount",
    )
    list_filter = ("created_at", "status", "movement_type", "category", "subcategory")
    search_fields = ("comment",)
