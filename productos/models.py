# productos/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from decimal import Decimal
from django.conf import settings # Asegúrate de que settings esté importado

# 1. Definición de Categoria
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
# productos/models.py
class ConfiguracionGlobal(models.Model):
    tasa_cambio_usd_mxn = models.DecimalField(max_digits=10, decimal_places=2, default=17.0)

    def __str__(self):
        return f"Tasa actual: {self.tasa_cambio_usd_mxn}"

    class Meta:
        verbose_name = "Configuración Global"
        verbose_name_plural = "Configuración Global"


# 2. Definición de Proveedor
class Proveedor(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    divisa_defecto = models.CharField(max_length=3, default='USD', help_text="Divisa por defecto de las listas de precios de este proveedor (ej. USD, EUR)")
    tasa_cambio_usd_mxn = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('1.0000'),
        help_text="Tipo de cambio específico de USD a MXN para este proveedor."
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"


# 3. Definición de TipoCambio
class TipoCambio(models.Model):
    divisa_origen = models.CharField(max_length=3, unique=True, help_text="Ej. USD")
    divisa_destino = models.CharField(max_length=3, default='MXN', help_text="Ej. MXN")
    valor = models.DecimalField(max_digits=10, decimal_places=4, help_text="Valor de 1 unidad de divisa_origen en divisa_destino")
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"1 {self.divisa_origen} = {self.valor} {self.divisa_destino}"

    class Meta:
        verbose_name = "Tipo de Cambio"
        verbose_name_plural = "Tipos de Cambio"
        ordering = ['-fecha_actualizacion']


# 4. Definición de Producto
class Producto(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    stock = models.IntegerField(default=0)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precio_dolar = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                       help_text="Precio original del producto en la divisa del proveedor")
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    inventario = models.IntegerField(default=0, null=True, blank=True)
    activo = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='productos_imagenes/', null=True, blank=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo_fabricante = models.CharField(max_length=100, blank=True, null=True)
    compatibilidad = models.TextField(blank=True, null=True)
    garantia_meses = models.IntegerField(blank=True, null=True)
    peso_kg = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    # Campos para componentes específicos
    num_nucleos = models.IntegerField(blank=True, null=True)
    velocidad_ghz = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    memoria_gb = models.IntegerField(blank=True, null=True)
    tipo_memoria = models.CharField(max_length=50, blank=True, null=True)
    capacidad_gb = models.IntegerField(blank=True, null=True)
    velocidad_mhz = models.IntegerField(blank=True, null=True)
    tipo_ram = models.CharField(max_length=50, blank=True, null=True)

    @property
    def precio_mxn(self):
        precio_base_mxn = Decimal(0)

        if self.precio_dolar is not None and self.precio_dolar > 0 and self.proveedor:
            tasa_cambio = self.proveedor.tasa_cambio_usd_mxn
            precio_base_mxn = self.precio_dolar * tasa_cambio
        elif self.precio is not None and self.precio > 0:
            precio_base_mxn = self.precio
        else:
            return Decimal(0)

        try:
            iva_rate = settings.IVA_RATE
            precio_con_iva = precio_base_mxn * (Decimal('1') + iva_rate)
            return precio_con_iva.quantize(Decimal('0.01'))
        except AttributeError:
            return precio_base_mxn.quantize(Decimal('0.01'))
        except Exception as e:
            return precio_base_mxn.quantize(Decimal('0.01'))

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"


# --- MODELOS PARA EL CHAT ---
class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                             help_text="Usuario registrado que inició la conversación, si aplica.")
    session_key = models.CharField(max_length=40, null=True, blank=True,
                                   help_text="Clave de sesión para usuarios anónimos.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_closed = models.BooleanField(default=False)
    user_display_name = models.CharField(max_length=100, blank=True, null=True,
                                         help_text="Nombre que el usuario proporcionó al iniciar el chat.")
    initial_message_text = models.TextField(blank=True, null=True,
                                            help_text="Primer mensaje/duda inicial del usuario.")

    def __str__(self):
        if self.user_display_name:
            return f"Conversación con {self.user_display_name}"
        elif self.user:
            return f"Conversación con {self.user.username}"
        elif self.session_key:
            return f"Conversación anónima ({self.session_key[:8]}...)"
        return f"Conversación #{self.id}"

class ChatMessage(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender_is_admin = models.BooleanField(default=False, help_text="True si el mensaje es del administrador.")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        sender = "Admin" if self.sender_is_admin else "Usuario"
        return f"{sender} ({self.timestamp.strftime('%H:%M')}): {self.message[:50]}..."