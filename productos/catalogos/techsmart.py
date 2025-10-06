import os
import re
from PyPDF2 import PdfReader
from productos.models import Producto, Proveedor, ProveedorPrecio
from core.utils import convertir_a_mxn, get_tasa_dolar

def procesar_catalogo_techsmart(ruta_archivo):
    print("📥 Procesando catálogo Techsmart:", ruta_archivo)

    if not os.path.exists(ruta_archivo):
        print(f"❌ El archivo {ruta_archivo} no existe.")
        return

    reader = PdfReader(ruta_archivo)
    proveedor, _ = Proveedor.objects.get_or_create(nombre="Techsmart")
    tasa_dolar = get_tasa_dolar()

    for page in reader.pages:
        text = page.extract_text()
        if not text:
            continue

        lines = text.split("\n")
        for line in lines:
            match = re.search(
                r'(?P<sku>[A-Z0-9\-]+)\s+(?P<nombre>.*?)\s+(?P<precio>\d+(?:,\d{3})*\.\d{2})\s+(?P<moneda>USD|MXN)',
                line
            )

            if match:
                sku = match.group('sku')
                precio = float(match.group('precio').replace(',', ''))
                moneda = match.group('moneda')

                try:
                    producto = Producto.objects.get(sku=sku)
                except Producto.DoesNotExist:
                    continue

                if moneda == "USD":
                    precio = convertir_a_mxn(precio, tasa_dolar)

                ProveedorPrecio.objects.update_or_create(
                    producto=producto,
                    proveedor=proveedor,
                    defaults={
                        'precio': precio,
                        'stock': 5,  # ajusta si tienes lógica real
                        'moneda': 'MXN'
                    }
                )
                print(f"✅ SKU {sku} actualizado.")
    
    print("✅ Catálogo Techsmart procesado.")
