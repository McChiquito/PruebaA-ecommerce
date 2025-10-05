import os
import re
from django.core.management.base import BaseCommand
from productos.models import Producto, Proveedor, ProveedorPrecio
from core.utils import convertir_a_mxn, get_tasa_dolar
from PyPDF2 import PdfReader


class Command(BaseCommand):
    help = 'Procesa el catálogo PDF de Techsmart y actualiza precios y stock.'

    def handle(self, *args, **options):
        print("🔍 Buscando archivo PDF de Techsmart...")
        ruta_pdf = "documentos/techsmart_catalogo.pdf"
        
        if not os.path.exists(ruta_pdf):
            print(f"❌ El archivo {ruta_pdf} no existe.")
            return

        print("📖 Abriendo archivo PDF...")
        reader = PdfReader(ruta_pdf)

        proveedor, _ = Proveedor.objects.get_or_create(nombre="Techsmart")
        print("✅ Proveedor Techsmart obtenido o creado.")

        tasa_dolar = get_tasa_dolar()
        print(f"💱 Tasa de dólar actual: {tasa_dolar}")

        print("🧠 Procesando páginas del PDF...")
        for num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if not text:
                print(f"⚠️ Página {num} vacía o no reconocible.")
                continue

            lines = text.split("\n")
            for line in lines:
                line = line.strip()

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
                        print(f"❌ SKU no encontrado en la base de datos: {sku}")
                        continue

                    if moneda == "USD":
                        precio = convertir_a_mxn(precio, tasa_dolar)

                    ProveedorPrecio.objects.update_or_create(
                        producto=producto,
                        proveedor=proveedor,
                        defaults={
                            'precio': precio,
                            'stock': 5,  # ❗ O ajustar con tu lógica real
                            'moneda': 'MXN',
                        }
                    )
                    print(f"✅ Precio actualizado para SKU {sku}: ${precio} MXN")
                else:
                    print(f"⏭️ Línea no reconocida en página {num}: {line}")
        
        print("🎉 Catálogo Techsmart actualizado correctamente.")
