# productos/management/commands/actualizar_proce.py
from django.core.management.base import BaseCommand
from productos.models import Producto, ProveedorPrecio
import pandas as pd
from productos.models import Producto, Proveedor, ProveedorPrecio

def procesar_catalogo_proce(ruta_archivo):
    print("📥 Procesando catálogo Proce:", ruta_archivo)
    df = pd.read_excel(ruta_archivo)
    proveedor, _ = Proveedor.objects.get_or_create(nombre="Proce")

    for _, row in df.iterrows():
        sku = str(row.get("SKU")).strip()
        precio = row.get("PRECIOS PESOS NETOS")
        stock = row.get("Inventario")

        try:
            producto = Producto.objects.get(sku=sku)
        except Producto.DoesNotExist:
            print(f"❌ SKU no encontrado: {sku}")
            continue

        ProveedorPrecio.objects.update_or_create(
            producto=producto,
            proveedor=proveedor,
            defaults={
                'precio': precio,
                'stock': stock,
                'moneda': 'MXN'
            }
        )
        print(f"✅ SKU {sku} actualizado.")
    
    print("✅ Catálogo Proce procesado.")

