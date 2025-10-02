# productos/management/commands/actualizar_arroba.py

from django.core.management.base import BaseCommand
from productos.utils.actualizar_desde_arroba import actualizar_datos_desde_arroba

class Command(BaseCommand):
    help = 'Actualiza productos desde el catálogo de Arroba'

    def add_arguments(self, parser):
        parser.add_argument('ruta_excel', type=str, help='Ruta al archivo Excel de Arroba')

    def handle(self, *args, **kwargs):
        ruta_excel = kwargs['ruta_excel']
        self.stdout.write(f'📥 Procesando archivo: {ruta_excel}')
        
        try:
            actualizar_datos_desde_arroba(ruta_excel)
            self.stdout.write(self.style.SUCCESS('✅ Actualización finalizada sin errores críticos.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error al ejecutar: {e}'))
