# ==========================================================
# productos/models.py — Modelos principales del e-commerce
# ==========================================================

from django.db import models
from django.utils.text import slugify
from django.conf import settings


# ==========================================================
# 1️⃣  MODELO DE CATEGORÍAS
# ==========================================================
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


# ==========================================================
# 2️⃣  MODELO DE PROVEEDORES
# ==========================================================
class Proveedor(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    tasa_cambio_usd_mxn = models.FloatField(
        default=18.0,
        help_text="Tasa de cambio específica de este proveedor"
    )
    incluye_iva = models.BooleanField(default=True, help_text="Indica si los precios del catálogo ya incluyen IVA")
    porcentaje_iva = models.FloatField(default=16.0, help_text="Porcentaje de IVA aplicable si no está incluido")


    class Meta:
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return f"{self.nombre} (Tasa: {self.tasa_cambio_usd_mxn})"


# ==========================================================
# 3️⃣  CONFIGURACIÓN GLOBAL
# ==========================================================
class ConfiguracionGlobal(models.Model):
    """
    Define valores globales del sistema, como la tasa de cambio global.
    """
    tasa_cambio_usd_mxn = models.FloatField(
        default=18.0,
        help_text="Tasa global de cambio USD a MXN"
    )

    class Meta:
        verbose_name = "Configuración Global"
        verbose_name_plural = "Configuración Global"

    def __str__(self):
        return f"Tasa: {self.tasa_cambio_usd_mxn}"


# ==========================================================
# 4️⃣  PRODUCTOS
# ==========================================================
class Producto(models.Model):
    nombre = models.CharField(max_length=255, blank=True, null=True)  # <— NUEVO
    sku = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    precio_dolar = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    garantia = models.CharField(max_length=100, blank=True, null=True)
    condicion = models.CharField(max_length=100, blank=True, null=True)
    imagen = models.ImageField(upload_to="productos_imagenes/", blank=True, null=True)
    stock = models.IntegerField(default=0)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.sku} - {self.descripcion}"
    
    @property
    def display_name(self):
        # útil si quieres exponerlo en el API
        return self.nombre or self.descripcion or self.sku
    @property
    def precio_mxn(self):
        """
        Calcula el precio del producto en MXN con base en la tasa del proveedor
        o el precio establecido en pesos.
        """
        from decimal import Decimal

        precio_base = Decimal(0)
        if self.precio_dolar and self.proveedor:
            precio_base = Decimal(self.precio_dolar) * Decimal(self.proveedor.tasa_cambio_usd_mxn)
        elif self.precio:
            precio_base = Decimal(self.precio)

        if precio_base <= 0:
            return Decimal("0.00")

        try:
            iva_rate = getattr(settings, "IVA_RATE", Decimal("0.00"))
            precio_final = precio_base * (Decimal("1") + iva_rate)
            return precio_final.quantize(Decimal("0.01"))
        except Exception:
            return precio_base.quantize(Decimal("0.01"))


# ==========================================================
# 5️⃣  PRECIOS POR PROVEEDOR (RELACIÓN INTERMEDIA)
# ==========================================================
class ProveedorPrecio(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    precio = models.FloatField(default=0.0)
    stock = models.IntegerField(default=0)
    moneda = models.CharField(max_length=10, default="MXN")

    class Meta:
        verbose_name_plural = "Precios por Proveedor"
        unique_together = ("producto", "proveedor")

    def __str__(self):
        return f"{self.proveedor.nombre} - {self.producto.sku}"

    @property
    def precio_mxn(self):
        from .models import ConfiguracionGlobal
        config = ConfiguracionGlobal.objects.first()
        tasa = config.tasa_cambio_usd_mxn if config else 18.0
        return round(self.precio * tasa, 2) if self.moneda == "USD" else self.precio


# ==========================================================
# 6️⃣  TIPO DE CAMBIO HISTÓRICO (opcional)
# ==========================================================
class TipoCambio(models.Model):
    fecha = models.DateField(auto_now_add=True)
    tasa_usd_mxn = models.FloatField(default=18.0)

    class Meta:
        verbose_name_plural = "Historial de Tipos de Cambio"

    def __str__(self):
        return f"{self.fecha} — {self.tasa_usd_mxn}"


# ==========================================================
# 7️⃣  CHAT DE SOPORTE (CONVERSACIONES)
# ==========================================================
class Conversation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    initial_message_text = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Conversaciones"

    def __str__(self):
        return f"Conversación #{self.id} — {self.created_at.strftime('%d/%m/%Y %H:%M')}"


class ChatMessage(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    text = models.TextField()
    sender = models.CharField(max_length=50, choices=[("user", "Usuario"), ("admin", "Administrador")])
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Mensajes del Chat"

    def __str__(self):
        return f"[{self.sender}] {self.text[:40]}"
# ==========================================================