# core/views.py

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

# Importa tus modelos y serializadores
# (Asegúrate de crear estos archivos y modelos primero)
from .models import Product, Category, Cart, CartItem, Invoice
from .serializers import (
    UserSerializer, 
    ProductSerializer, 
    CategorySerializer, 
    CartItemSerializer,
    CartSerializer
)

# --- Vistas de Autenticación y Registro ---

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny] # Cualquiera puede registrarse

# --- Vistas del Catálogo de Productos ---

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para ver las categorías de productos.
    Solo permite leer (listar y ver detalle).
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny] # Cualquiera puede ver las categorías

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para ver los productos.
    Solo permite leer (listar y ver detalle).
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny] # Cualquiera puede ver los productos

# --- Vistas del Carrito de Compras ---

class CartView(APIView):
    """
    Vista para ver y gestionar el carrito del usuario actual.
    """
    permission_classes = [IsAuthenticated] # Solo usuarios logueados

    def get(self, request):
        # Busca un carrito para el usuario, si no existe, lo crea.
        cart, created = Cart.objects.get_or_create(user=request.user, ordered=False)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AddItemToCartView(APIView):
    """
    Vista para agregar un producto al carrito.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id:
            return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user, ordered=False)

        # Revisa si el item ya está en el carrito para actualizar la cantidad
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        
        cart_item.save()
        return Response({"success": f"'{product.name}' fue añadido al carrito."}, status=status.HTTP_200_OK)

class RemoveItemFromCartView(APIView):
    """
    Vista para eliminar un producto del carrito.
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

# --- Vista de Checkout ---

class CheckoutView(APIView):
    """
    Vista para procesar la compra.
    Aquí es donde se integra LangGraph.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user, ordered=False)
        
        if not cart.items.exists():
            return Response({"error": "Tu carrito está vacío."}, status=status.HTTP_400_BAD_REQUEST)
        
        # ==========================================================
        # AQUÍ VA LA LÓGICA PARA LLAMAR A TU AGENTE DE LANGGRAPH
        # ==========================================================
        # 1. Recopila la información necesaria (usuario, items del carrito).
        # 2. Inicia tu grafo de LangGraph con esa información.
        #    ej: result = run_checkout_agent(user_id=request.user.id, cart_id=cart.id)
        # 3. El agente debería encargarse de crear la Factura (Invoice),
        #    vaciar el carrito, etc.
        # 4. Devuelve el resultado del agente.
        
        # --- Simulación del proceso por ahora ---
        # Marcar el carrito como "ordenado" para que no se pueda volver a usar.
        cart.ordered = True
        cart.save()

        # Crear una nueva factura (esto lo haría el agente de LangGraph)
        invoice = Invoice.objects.create(user=request.user, total_amount=cart.get_total()) # (Necesitarás un método get_total en tu modelo Cart)
        
        return Response({
            "success": "Tu compra fue procesada exitosamente.",
            "invoice_id": invoice.id,
            "total": invoice.total_amount
        }, status=status.HTTP_200_OK)