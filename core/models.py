# core/models.py

from django.db import models
from django.contrib.auth.models import User

# --- Modelos del Catálogo ---

class Category(models.Model):
    """Modelo para las categorías de productos."""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories" # Para que en el admin no diga "Categorys"

    def __str__(self):
        return self.name

class Product(models.Model):
    """Modelo para los productos."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

# --- Modelos del Carrito y Compra ---

class Cart(models.Model):
    """Modelo para el carrito de compras de un usuario."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total(self):
        """Calcula el costo total de todos los items en el carrito."""
        total = 0
        for item in self.items.all():
            total += item.get_subtotal()
        return total

    def __str__(self):
        return f"Carrito de {self.user.username}"

class CartItem(models.Model):
    """Modelo que representa un producto dentro de un carrito."""
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_subtotal(self):
        """Calcula el costo total para este item (precio * cantidad)."""
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name} en {self.cart}"

class Invoice(models.Model):
    """Modelo para guardar el registro de una compra (factura)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Podrías enlazarlo al carrito original si quisieras:
    # cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Factura #{self.id} para {self.user.username}"

# Nota: Para un sistema más completo, podrías crear un modelo 'InvoiceItem'
# para guardar una copia estática de los productos y precios al momento de la compra.
# Esto evita que la factura cambie si un producto es eliminado o su precio cambia en el futuro.