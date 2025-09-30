# bakery/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # other bakery urls...
    path("get-products/", views.get_products, name="get_products"),
]
