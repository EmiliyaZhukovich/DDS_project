from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Status(models.Model):
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'

    def __str__(self) -> str:
        return self.name

class MovementType(models.Model):
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        verbose_name = 'Тип операции'
        verbose_name_plural = 'Типы операций'

    def __str__(self) -> str:
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=128)
    movement_type = models.ForeignKey(
        MovementType,
        on_delete=models.CASCADE,
        related_name='categories',
    )

    class Meta:
        unique_together = ('name', 'movement_type')
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        f"{self.name} ({self.movement_type})"

class SubCategory(models.Model):
    name = models.CharField(max_length=128)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories',
    )

    class Meta:
        unique_together = ('name', 'category')
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'

    def __str__(self) -> str:
        f"{self.name} ({self.category})"

class Movement(models.Model):
    created_at = models.DateField(default=timezone.now)
    status = models.ForeignKey(Status, on_delete=models.PROTECT, related_name='movements')
    movement_type = models.ForeignKey(MovementType, on_delete=models.PROTECT, related_name='movements')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='movements')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.PROTECT, related_name='movements')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at', 'id']
        verbose_name = 'Операция ДДС'
        verbose_name_plural = 'Операции ДДС'

    def __str__(self) -> str:
        return f"{self.created_at} {self.movement_type} {self.category}/{self.subcategory}: {self.amount}"

    def clean(self) -> None:
        # Validate category belongs to movement_type
        if self.category and self.movement_type and self.category.movement_type_id != self.movement_type_id:
            raise ValidationError({
                "category": "Категория должна относиться к выбранному типу.",
                "movement_type": "Тип должен соответствовать категории.",
            })
        # Validate subcategory belongs to category
        if self.subcategory and self.category and self.subcategory.category_id != self.category_id:
            raise ValidationError({
                "subcategory": "Подкатегория должна относиться к выбранной категории.",
                "category": "Категория должна соответствовать подкатегории.",
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
