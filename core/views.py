from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

# --- Modelos, Serializers y Servicios ---
from .models import Product, Category, Cart, CartItem, Invoice
from .serializers import (
    UserSerializer, 
    ProductSerializer, 
    CategorySerializer, 
    CartItemSerializer,
    CartSerializer
)
from .services.checkout_agent import run_checkout_agent
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm

class UserCreateView(generics.CreateAPIView):
    """
    Vista de API para que nuevos usuarios se registren.
    Solo permite peticiones POST.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de API para ver las categorías de productos.
    Solo permite leer (listar y ver detalle).
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de API para ver los productos.
    Solo permite leer (listar y ver detalle).
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

class CartView(APIView):
    """
    Vista de API para ver y gestionar el carrito del usuario actual.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user, ordered=False)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AddItemToCartView(APIView):
    """
    Vista de API para agregar un producto al carrito.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id:
            return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user, ordered=False)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        
        cart_item.save()
        return Response({"success": f"'{product.name}' fue añadido al carrito."}, status=status.HTTP_200_OK)

class RemoveItemFromCartView(APIView):
    """
    Vista de API para eliminar un producto del carrito.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        cart = get_object_or_404(Cart, user=request.user, ordered=False)
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.delete()
            return Response({"success": f"'{product.name}' fue eliminado del carrito."}, status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({"error": "Este item no se encuentra en tu carrito."}, status=status.HTTP_404_NOT_FOUND)

class CheckoutView(APIView):
    """
    Vista de API para procesar la compra con el agente de LangGraph.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            cart = Cart.objects.get(user=request.user, ordered=False)
        except Cart.DoesNotExist:
             return Response({"error": "No tienes un carrito activo."}, status=status.HTTP_404_NOT_FOUND)
        
        result_state = run_checkout_agent(user_id=request.user.id, cart_id=cart.id)
        
        if result_state.get('error'):
            return Response({"error": result_state.get('message')}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "success": result_state.get('message'),
            "invoice_id": result_state.get('invoice_id')
        }, status=status.HTTP_200_OK)


# ====================================================================
#                  VISTAS PARA EL FRONTEND (CON PLANTILLAS)
# ====================================================================

def product_list_view(request):
    """
    Esta vista muestra los productos y maneja la adición al carrito desde el frontend.
    """
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('login') # (Crearemos la URL 'login' pronto)

        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user, ordered=False)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1
        else:
            cart_item.quantity = 1 
        
        cart_item.save()
        return redirect('product-list')

    products = Product.objects.all()
    context = {
        'products': products
    }
    return render(request, 'core/product_list.html', context)
 
def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST) # <-- CAMBIO AQUÍ
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "¡Registro exitoso!")
            return redirect("product-list")
        else:
            messages.error(request, "Información inválida. Por favor, corrige los errores.")
    else:
        form = CustomUserCreationForm() # <-- CAMBIO AQUÍ
    return render(request, "core/register.html", {"form": form})

# Y ahora la vista de login
def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST) # <-- CAMBIO AQUÍ
        if form.is_valid():
            # ... (el resto de la vista no cambia) ...
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Bienvenido de nuevo, {username}.")
                return redirect("product-list")
            else:
                messages.error(request, "Usuario o contraseña inválidos.")
        else:
            messages.error(request, "Usuario o contraseña inválidos.")
    form = CustomAuthenticationForm() # <-- CAMBIO AQUÍ
    return render(request, "core/login.html", {"form": form})

def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión exitosamente.")
    return redirect("product-list")
 
@login_required(login_url='/login/')
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user, ordered=False)

    if request.method == 'POST':
        # --- Lógica para manejar acciones del carrito ---
        if 'remove_item' in request.POST:
            item_id = request.POST.get('item_id')
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            cart_item.delete()
            messages.success(request, "Item eliminado del carrito.")
        
        elif 'checkout' in request.POST:
            if not cart.items.exists():
                messages.error(request, "Tu carrito está vacío.")
                return redirect('cart')

            # --- AQUÍ SE ACTIVA EL AGENTE DE LANGGRAPH ---
            result_state = run_checkout_agent(user_id=request.user.id, cart_id=cart.id)
            
            if result_state.get('error'):
                messages.error(request, f"Error en el pago: {result_state.get('message')}")
            else:
                messages.success(request, f"¡Compra exitosa! {result_state.get('message')}")
            
            return redirect('product-list')

        return redirect('cart')

    context = {
        'cart': cart
    }
    return render(request, 'core/cart.html', context)