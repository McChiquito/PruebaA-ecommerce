# productos/management/commands/actualizar_proce.py
from django.core.management.base import BaseCommand
from productos.models import Producto, ProveedorPrecio
import pandas as pd

class Command(BaseCommand):
    help = "Actualiza precios e inventario desde Proce"

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Ruta al archivo Excel')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file']

        # Lee el excel desde la fila 3 como cabecera
        df = pd.read_excel(file_path, header=2)

        actualizados = 0
        no_encontrados = 0

        for _, row in df.iterrows():
            sku = str(row.get('SKU', '')).strip()
            inventario = row.get('Inventario', 0)
            precio = row.get('PRECIOS PESOS NETOS', 0)

            # 🔥 Normaliza NaN / None
            if pd.isna(inventario):
                inventario = 0
            if pd.isna(precio):
                precio = 0

            try:
                producto = Producto.objects.get(sku=sku)

                ProveedorPrecio.objects.update_or_create(
                    producto=producto,
                    proveedor="Proce",
                    defaults={
                        'precio': precio,
                        'stock': inventario
                    }
                )
                actualizados += 1
            except Producto.DoesNotExist:
                no_encontrados += 1

        self.stdout.write(self.style.SUCCESS("Actualización finalizada."))
        self.stdout.write(self.style.SUCCESS(f"Productos actualizados: {actualizados}"))
        self.stdout.write(self.style.WARNING(f"SKUs no encontrados en la base: {no_encontrados}"))
