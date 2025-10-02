# productos/management/commands/update_productos_from_excel.py

import openpyxl
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from productos.models import Producto, Categoria, Proveedor # Asegúrate de que Proveedor y Categoria están importados
from decimal import Decimal

class Command(BaseCommand):
    help = 'Actualiza inventario y precio_dolar de productos existentes basado en un archivo Excel.'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='La ruta al archivo Excel a procesar')

    def handle(self, *args, **options):
        excel_file_path = options['excel_file']
        self.stdout.write(self.style.NOTICE(f"Iniciando la actualización desde {excel_file_path}"))

        try:
            workbook = openpyxl.load_workbook(excel_file_path)
            sheet = workbook.active
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Error: El archivo '{excel_file_path}' no fue encontrado."))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al abrir el archivo Excel: {e}"))
            return

        # --- Obtener encabezados y convertirlos a minúsculas ---
        header = [cell.value.lower() if cell.value else '' for cell in sheet[1]]

        data_rows = []
        for row_num_excel, row_data in enumerate(sheet.iter_rows(min_row=2, values_only=True)):
            row_dict = {}
            for col_num, cell_value in enumerate(row_data):
                if col_num < len(header):
                    header_name = header[col_num]
                    # Limpia el nombre del encabezado (reemplaza espacios y caracteres especiales)
                    header_name = header_name.replace(' ', '_').replace('.', '').replace('/', '_').strip()
                    row_dict[header_name] = cell_value
            data_rows.append(row_dict)

        with transaction.atomic():
            updated_count = 0
            skipped_count = 0

            for row_index, row_dict in enumerate(data_rows):
                # row_num_display es para mostrar el número de fila del Excel original (empieza en 2)
                row_num_display = row_index + 2

                sku = row_dict.get('sku')
                
                # Intentar obtener el precio del dólar de varias columnas posibles
                precio_dolar_excel = row_dict.get('precio_en_dolar')
                if precio_dolar_excel is None:
                    precio_dolar_excel = row_dict.get('precio_dolar')
                # También podrías considerar 'precio_dólar' o variantes con tildes si tu Excel las usa
                if precio_dolar_excel is None:
                    precio_dolar_excel = row_dict.get('precio_en_dólar') # Añadido por si hay tilde

                inventario_excel = row_dict.get('inventario')

                # --- LÍNEA DE DEPURACIÓN (YA INCLUIDA) ---
                self.stdout.write(f'DEBUG: Fila {row_num_display} (SKU: {sku}) - Raw precio_dolar_excel: "{precio_dolar_excel}" (Tipo: {type(precio_dolar_excel)})')
                # ------------------------------------------

                if not sku:
                    self.stdout.write(self.style.WARNING(f'Fila {row_num_display}: SKU vacío, saltando.'))
                    skipped_count += 1
                    continue

                try:
                    producto = Producto.objects.get(sku=sku)

                    if precio_dolar_excel is not None and str(precio_dolar_excel).strip() != '':
                        try:
                            producto.precio_dolar = Decimal(str(precio_dolar_excel).replace(',', '')) # Asegura conversión a string y maneja comas
                            self.stdout.write(f'DEBUG: Fila {row_num_display} (SKU: {sku}): Precio Dólar procesado a Decimal: {producto.precio_dolar}')
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f"Fila {row_num_display} (SKU: {sku}): No se pudo convertir 'precio_dolar' '{precio_dolar_excel}' a Decimal. Error: {e}"))
                    else:
                        self.stdout.write(f'DEBUG: Fila {row_num_display} (SKU: {sku}): precio_dolar_excel es None o vacío, no se actualiza.')


                    if inventario_excel is not None and str(inventario_excel).strip() != '':
                        try:
                            producto.inventario = int(float(str(inventario_excel))) # Convertir a float primero para manejar números con decimales como '2.0'
                            self.stdout.write(f'DEBUG: Fila {row_num_display} (SKU: {sku}): Inventario procesado a Entero: {producto.inventario}')
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f"Fila {row_num_display} (SKU: {sku}): No se pudo convertir 'inventario' '{inventario_excel}' a entero. Error: {e}"))
                    else:
                        self.stdout.write(f'DEBUG: Fila {row_num_display} (SKU: {sku}): inventario_excel es None o vacío, no se actualiza.')


                    producto.save()
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Fila {row_num_display} (SKU: {sku}): Actualizado precio_dolar e inventario."))

                except Producto.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Fila {row_num_display} (SKU: {sku}): Producto no encontrado en la base de datos, saltando actualización."))
                    skipped_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Fila {row_num_display} (SKU: {sku}): Error inesperado al procesar: {e}"))
                    skipped_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Proceso de actualización completado. Productos actualizados: {updated_count}. Productos saltados: {skipped_count}."
        ))