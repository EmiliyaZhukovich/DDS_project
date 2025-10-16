from django import forms
from django.views import View
from django.utils.dateparse import parse_date
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.utils import timezone

from .models import Status, MovementType, Category, SubCategory, Movement

class MovementForm(forms.ModelForm):
    created_at = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type':'date'}),
        initial=timezone.now
    )

    class Meta:
        model = Movement
        fields = [
            'created_at',
            'status',
            'movement_type',
            'category',
            'subcategory',
            'amount',
            'comment',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        movement_type = None
        category = None
        if self.is_bound:
            mt_id = self.data.get('movement_type')
            cat_id = self.data.get('category')
            if mt_id:
                movement_type = MovementType.objects.filter(pk=mt_id).first()
            if cat_id:
                category = Category.objects.filter(pk=cat_id).first()
        else:
            instance: Movement | None = self.instance if hasattr(self, 'instance') else None
            movement_type = getattr(instance, 'movement_type', None)
            category = getattr(instance, 'category', None)

        if movement_type:
            self.fields['category'].queryset = Category.objects.filter(movement_type=movement_type)
        else:
            self.fields['category'].queryset = Category.objects.none()

        if category:
            self.fields['subcategory'].queryset = SubCategory.objects.filter(category=category)
        else:
            self.fields['subcategory'].queryset = SubCategory.objects.none()

    def clean_created_at(self):
        created_at = self.cleaned_data.get('created_at')
        if not created_at:
            return timezone.now().date()
        return created_at

class MovementListView(View):
    def get(self, request):
        qs = Movement.objects.select_related(
            'status', 'movement_type', 'category', 'subcategory'
        ).all()

        date_from = parse_date(request.GET.get('date_from') or '')
        date_to = parse_date(request.GET.get('date_to') or '')
        status_id = request.GET.get('status')
        mt_id = request.GET.get('movement_type')
        category_id = request.GET.get('category')
        subcategory_id = request.GET.get('subcategory')

        if date_from:
            qs = qs.filter(created_at__gte = date_from)
        if date_to:
            qs = qs.filter(created_at__lte = date_to)
        if status_id:
            qs = qs.filter(status_id = status_id)
        if mt_id:
            qs = qs.filter(movement_type_id = mt_id)
        if category_id:
            qs = qs.filter(category_id = category_id)
        if subcategory_id:
            qs = qs.filter(subcategory_id = subcategory_id)

        paginator = Paginator(qs, 20)
        page = request.GET.get('page')
        page_obj = paginator.get_page(page)

        context = {
            "page_obj": page_obj,
            "statuses": Status.objects.all(),
            "movement_types": MovementType.objects.all(),
            "categories": Category.objects.all(),
            "subcategories": SubCategory.objects.all(),
            "filters": {
                "date_from": request.GET.get("date_from", ""),
                "date_to": request.GET.get("date_to", ""),
                "status": status_id or "",
                "movement_type": mt_id or "",
                "category": category_id or "",
                "subcategory": subcategory_id or "",
            },
        }
        return render(request, 'dds/movement_list.html', context)

class MovementCreateView(View):
    def get(self, request):
        form = MovementForm()
        return render(request, 'dds/movement_form.html', {'form':form})

    def post(self, request):
        form = MovementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('movement_list'))
        return render(request, 'dds/movement_form.html', {'form':form})

class MovementUpdateView(View):
    def get(self, request, pk):
        movement = get_object_or_404(Movement, pk=pk)
        form = MovementForm(instance=movement)
        return render(request, 'dds/movement_form.html', {'form': form, 'movement': movement})

    def post(self, request, pk):
        movement = get_object_or_404(Movement, pk=pk)
        form = MovementForm(request.POST, instance=movement)
        if form.is_valid():
            form.save()
            return redirect(reverse('movement_list'))
        return render(request, 'dds/movement_form.html', {'form': form, 'movement': movement})

class MovementDeleteView(View):
    def post(self, request, pk):
        movement = get_object_or_404(Movement, pk=pk)
        movement.delete()
        return redirect(reverse('movement_list'))

def categories_by_type(request):
    mt_id = request.GET.get('movement_type')
    categories = Category.objects.filter(movement_type_id = mt_id).values('id', 'name') if mt_id else []
    return JsonResponse({'result':list(categories)})

def subcategories_by_category(request):
    cat_id = request.GET.get('category')
    subcategories = SubCategory.objects.filter(category_id=cat_id).values('id', 'name') if cat_id else []
    return JsonResponse({'result':list(subcategories)})

