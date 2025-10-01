import pandas as pd
from django.core.management.base import BaseCommand
from productos.models import Producto, Proveedor
from decimal import Decimal


class Command(BaseCommand):
    help = 'Importa productos desde el catálogo del Proveedor 1 (Excel)'


    def add_arguments(self, parser):
        parser.add_argument('archivo', type=str, help='Ruta al archivo Excel del proveedor')


    def handle(self, *args, **kwargs):
        archivo = kwargs['archivo']
        df = pd.read_excel(archivo, skiprows=4)


    proveedor, _ = Proveedor.objects.get_or_create(nombre="Proveedor 1")


    productos_creados = 0
    productos_actualizados = 0


    for _, row in df.iterrows():
        sku = row.get("Unnamed: 5") # Clave de artículo
        nombre = row.get("Unnamed: 6") # Descripción
        categoria = row.get("Unnamed: 3") # Departamento
        marca = row.get("Unnamed: 2")
        precio_mxn = row.get("Unnamed: 13") # Precio Final
        precio_dolar = row.get("Unnamed: 12") # Precio USD
        stock = row.get("Unnamed: 8") # CEDIS o inventario total


    if pd.isna(sku) or pd.isna(nombre):
        continue


    producto, creado = Producto.objects.update_or_create(
        sku=sku,
        defaults={
        'nombre': nombre,
        'descripcion': nombre,
        'precio': Decimal(precio_mxn) if not pd.isna(precio_mxn) else None,
        'precio_dolar': Decimal(precio_dolar) if not pd.isna(precio_dolar) else None,
        'marca': marca,
        'inventario': int(stock) if not pd.isna(stock) else 0,
        'proveedor': proveedor
        }
    )


    if creado:
        productos_creados += 1
    else:
        productos_actualizados += 1


    self.stdout.write(self.style.SUCCESS(f'✅ {productos_creados} productos creados.'))
    self.stdout.write(self.style.SUCCESS(f'♻️ {productos_actualizados} productos actualizados.'))
    self.stdout.write(self.style.SUCCESS('✅ Catálogo del proveedor 1 importado correctamente.'))