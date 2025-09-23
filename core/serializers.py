# core/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Category, Cart, CartItem

# --- Serializer para Registro de Usuario ---
class UserSerializer(serializers.ModelSerializer):
    """Serializer para crear nuevos usuarios."""
    class Meta:
        model = User
        # Campos que se usarán para crear un usuario
        fields = ['id', 'username', 'email', 'password']
        # 'password' es de solo escritura, no se debe mostrar al pedir datos
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Usamos create_user para que la contraseña se guarde hasheada (encriptada)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

# --- Serializers para el Catálogo ---
class CategorySerializer(serializers.ModelSerializer):
    """Serializer para el modelo Category."""
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Product."""
    # Para que en vez del ID de la categoría, muestre su nombre
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category']

# --- Serializers para el Carrito de Compras ---
class CartItemSerializer(serializers.ModelSerializer):
    """Serializer para los items dentro del carrito."""
    # Anidamos el serializer de Producto para mostrar toda su información
    product = ProductSerializer(read_only=True)
    # Mostramos el subtotal calculado desde el modelo
    subtotal = serializers.DecimalField(source='get_subtotal', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'subtotal']

class CartSerializer(serializers.ModelSerializer):
    """Serializer principal para el Carrito."""
    items = CartItemSerializer(many=True, read_only=True)
    # Mostramos el total calculado desde el modelo
    total = serializers.DecimalField(source='get_total', max_digits=10, decimal_places=2, read_only=True)

    # --- ESTA ES LA PARTE QUE FALTA O ESTÁ INCORRECTA ---
    class Meta:
        model = Cart
        fields = ['id', 'user', 'ordered', 'created_at', 'items', 'total']