from django.core.management.base import BaseCommand
from productos.models import Producto, Proveedor, ProveedorPrecio, ConfiguracionGlobal
import pdfplumber
import re


class Command(BaseCommand):
    help = 'Actualiza precios de productos desde archivo PDF de Techsmart'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Ruta al archivo PDF')

    def handle(self, *args, **options):
        pdf_path = options['file']
        if not pdf_path:
            self.stderr.write(self.style.ERROR("Debes proporcionar un archivo PDF con --file"))
            return

        try:
            tasa_dolar = ConfiguracionGlobal.objects.first().tasa_cambio_usd_mxn
            self.stdout.write(f"Tasa actual USD -> MXN: {tasa_dolar:.2f}")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"No se pudo obtener la tasa de cambio: {e}"))
            return

        # Obtener el proveedor "Techsmart"
        try:
            proveedor = Proveedor.objects.get(nombre="Techsmart")
        except Proveedor.DoesNotExist:
            self.stderr.write(self.style.ERROR("El proveedor 'Techsmart' no está registrado en la base de datos."))
            return

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue

                for line in text.split('\n'):
                    parts = re.split(r'\s{2,}', line.strip())
                    if len(parts) < 5:
                        continue  # Línea no válida

                    sku = parts[0].strip()
                    moneda = parts[-2].strip().upper()
                    precio_str = parts[-1].strip().replace('$', '').replace(',', '')

                    # Validar precio
                    try:
                        precio = float(precio_str)
                    except ValueError:
                        continue

                    # Convertir si es USD
                    if moneda == 'USD':
                        precio *= tasa_dolar
                    elif moneda != 'MXN':
                        continue  # Moneda no válida

                    try:
                        producto = Producto.objects.get(sku=sku)
                        ProveedorPrecio.objects.update_or_create(
                            producto=producto,
                            proveedor=proveedor,
                            defaults={'precio': round(precio, 2), 'stock': 1}
                        )
                    except Producto.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"❌ SKU no encontrado: {sku}"))

        self.stdout.write(self.style.SUCCESS("✅ Catálogo de Techsmart actualizado correctamente."))
