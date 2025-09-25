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
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm

# ====================================================================
#                          VISTAS PARA LA API (DRF)
# ====================================================================

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

class CartView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user, ordered=False)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AddItemToCartView(APIView):
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
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('login')
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user, ordered=False)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1
        else:
            cart_item.quantity = 1
        cart_item.save()
        messages.success(request, f"¡'{product.name}' se añadió a tu carrito!", extra_tags='added_to_cart_modal')
        return redirect('product-list-page') 

    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'core/product_list.html', context)
 
def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST) 
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "¡Registro exitoso!")
            return redirect("product-list-page")
        else:
            messages.error(request, "Información inválida. Por favor, corrige los errores.")
    else:
        form = CustomUserCreationForm() 
    return render(request, "core/register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST) 
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Bienvenido de nuevo, {username}.")
                return redirect("product-list-page")
            else:
                messages.error(request, "Usuario o contraseña inválidos.")
        else:
            messages.error(request, "Usuario o contraseña inválidos.")
    form = CustomAuthenticationForm()
    return render(request, "core/login.html", {"form": form})

def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión exitosamente.")
    return redirect("product-list-page") 

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user, ordered=False)
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        if item_id:
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            if 'increment_quantity' in request.POST:
                cart_item.quantity += 1
                cart_item.save()
                messages.success(request, f"Se actualizó la cantidad de '{cart_item.product.name}'.")
            elif 'decrement_quantity' in request.POST:
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                    messages.success(request, f"Se actualizó la cantidad de '{cart_item.product.name}'.")
                else:
                    product_name = cart_item.product.name
                    cart_item.delete()
                    messages.success(request, f"Se eliminó '{product_name}' del carrito.")
            elif 'remove_item' in request.POST:
                product_name = cart_item.product.name
                cart_item.delete()
                messages.success(request, f"Se eliminó '{product_name}' del carrito.")
        
        elif 'checkout' in request.POST:
            if not cart.items.exists():
                messages.error(request, "Tu carrito está vacío.")
                return redirect('cart')
            
            result_state = run_checkout_agent(user_id=request.user.id, cart_id=cart.id)
            
            if result_state.get('error'):
                messages.error(request, f"Error en el pago: {result_state.get('message')}")
                return redirect('cart') # Si hay error, nos quedamos en el carrito
            else:
                # CORRECCIÓN: Redirigir a la página de confirmación con el ID de la factura.
                invoice_id = result_state.get('invoice_id')
                # No necesitamos un mensaje aquí, la página de confirmación es el mensaje.
                return redirect('order-confirmation', invoice_id=invoice_id)

        return redirect('cart')

    context = {'cart': cart}
    return render(request, 'core/cart.html', context)

# --- VISTA NUEVA: Para la página de confirmación de compra ---
@login_required
def order_confirmation_view(request, invoice_id):
    """
    Muestra la página de confirmación después de una compra exitosa.
    """
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    context = {
        'invoice': invoice
    }
    return render(request, 'core/order_confirmation.html', context)