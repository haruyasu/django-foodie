from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('search', views.Search, name='search'),
    path('shop_info/<str:restid>', views.ShopInfo, name='shop_info')
]
