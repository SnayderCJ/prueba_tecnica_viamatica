# core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

# --- RUTAS DE LA API ---
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')

# Juntamos todas las URLs que pertenecen a la API
api_urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.UserCreateView.as_view(), name='user-register'),
    path('cart/', views.CartView.as_view(), name='cart-view'),
    path('cart/add-item/', views.AddItemToCartView.as_view(), name='cart-add-item'),
    path('cart/remove-item/<int:product_id>/', views.RemoveItemFromCartView.as_view(), name='cart-remove-item'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    
    # Rutas de login y refresh del token
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# --- RUTAS PRINCIPALES DE LA APP ---
urlpatterns = [
    path('productos/', views.product_list_view, name='product-list'),
    path('api/', include(api_urlpatterns)),
]