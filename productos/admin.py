from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.models import Sum
import os

from .models import (
    Categoria, Producto, Proveedor, ProveedorPrecio,
    ConfiguracionGlobal, TipoCambio
)
from .catalogos import arroba, proce, techsmart


# =============================
#   CONFIGURACIÓN GLOBAL
# =============================

@admin.register(ConfiguracionGlobal)
class ConfiguracionGlobalAdmin(admin.ModelAdmin):
    list_display = ('tasa_cambio_usd_mxn',)


@admin.register(TipoCambio)
class TipoCambioAdmin(admin.ModelAdmin):
    list_display = ('id', 'tasa_usd_mxn', 'fecha')
    search_fields = ('id',)
    list_filter = ('fecha',)
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    search_fields = ('nombre',)


# =============================
#   ADMIN PRODUCTOS
# =============================

class ProveedorPrecioInline(admin.TabularInline):
    """Muestra precios y stock por proveedor dentro del detalle del producto."""
    model = ProveedorPrecio
    extra = 0
    readonly_fields = ('proveedor', 'precio', 'stock')
    can_delete = False


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'sku',
        'nombre',
        'descripcion',
        'categoria',
        'mostrar_precios_por_proveedor',
        'stock_total',
        'creado',
        'actualizado',
    )
    search_fields = ('sku', 'descripcion')
    list_filter = ('categoria',)
    inlines = [ProveedorPrecioInline]

    def mostrar_precios_por_proveedor(self, obj):
        """Muestra precios agrupados por proveedor"""
        precios = ProveedorPrecio.objects.filter(producto=obj)
        if not precios.exists():
            return "— Sin precios cargados —"
        salida = []
        for p in precios:
            salida.append(f"{p.proveedor.nombre}: ${p.precio:,.2f} (Stock: {p.stock})")
        return "\n".join(salida)
    mostrar_precios_por_proveedor.short_description = "Precios por proveedor"

    def stock_total(self, obj):
        total = ProveedorPrecio.objects.filter(producto=obj).aggregate(total_stock=Sum('stock'))['total_stock']
        return total if total else 0
    stock_total.short_description = "Stock total"


# =============================
#   DASHBOARD DE ADMIN PERSONALIZADO
# =============================

# En Django 5, no se usa register_view. Usamos URLs normales desde views.py
# El dashboard está definido en productos/views.py -> admin_dashboard
# Por eso no necesitamos definir la clase AdminDashboard aquí.

# =============================
# CONFIG VISUAL DEL SITIO ADMIN
# =============================

admin.site.site_header = "MV STORE - Panel de Administración"
admin.site.site_title = "Panel Administrativo MV STORE"
admin.site.index_title = "Gestión de Productos y Proveedores"
