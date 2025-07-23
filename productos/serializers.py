# productos/serializers.py
from rest_framework import serializers
from .models import Producto, Categoria, Proveedor

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'slug']

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ['id', 'nombre']

class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    proveedor_nombre = serializers.CharField(source='proveedor.nombre', read_only=True)
    precio_mxn = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True) # Incluye tu propiedad

    class Meta:
        model = Producto
        fields = [
            'sku', 'nombre', 'descripcion', 'categoria', 'categoria_nombre',
            'precio', 'precio_dolar', 'proveedor', 'proveedor_nombre',
            'inventario', 'activo', 'imagen', 'marca', 'modelo_fabricante',
            'compatibilidad', 'garantia_meses', 'peso_kg',
            'num_nucleos', 'velocidad_ghz', 'memoria_gb', 'tipo_memoria',
            'capacidad_gb', 'velocidad_mhz', 'tipo_ram',
            'precio_mxn' # Asegúrate de incluirlo aquí
        ]