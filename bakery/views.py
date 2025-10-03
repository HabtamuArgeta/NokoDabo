from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Bread, Injera, Flour, Yeast, Enhancer

def home(request):
    return render(request, "home.html")

@require_GET
def get_products(request):
    product_type = request.GET.get("product_type")
    products = []
    if product_type == "bread":
        products = list(Bread.objects.values("id", "name"))
    elif product_type == "injera":
        products = list(Injera.objects.values("id", "name"))
    elif product_type == "flour":
        products = list(Flour.objects.values("id", "name"))
    elif product_type == "yeast":
        products = list(Yeast.objects.values("id", "name"))
    elif product_type == "enhancer":
        products = list(Enhancer.objects.values("id", "name"))
    return JsonResponse({"products": products})
