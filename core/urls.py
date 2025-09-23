from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')

# Las urlpatterns son la lista principal de rutas de nuestra aplicación.
urlpatterns = [
    # --- RUTAS GENERADAS POR EL ROUTER ---
    # Incluye las URLs generadas automáticamente para categorías y productos.
    path('', include(router.urls)),

    # --- RUTA DE REGISTRO DE USUARIOS ---
    # Un endpoint para que nuevos usuarios puedan crear una cuenta.
    path('register/', views.UserCreateView.as_view(), name='user-register'),

    # --- RUTAS DEL CARRITO DE COMPRAS ---
    # Rutas específicas para manejar la lógica del carrito.
    path('cart/', views.CartView.as_view(), name='cart-view'),
    path('cart/add-item/', views.AddItemToCartView.as_view(), name='cart-add-item'),
    path('cart/remove-item/<int:product_id>/', views.RemoveItemFromCartView.as_view(), name='cart-remove-item'),
    
    # --- RUTA DE CHECKOUT (COMPRA) ---
    # El endpoint que recibirá la señal de compra e iniciará el agente de LangGraph.
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
]