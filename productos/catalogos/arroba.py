# productos/management/commands/actualizar_arroba.py

from django.core.management.base import BaseCommand
from productos.utils.actualizar_desde_arroba import actualizar_datos_desde_arroba
from productos.models import ConfiguracionGlobal


def procesar_catalogo_arroba(ruta_archivo):
    print("📥 Procesando catálogo Arroba:", ruta_archivo)
    actualizar_datos_desde_arroba(ruta_archivo)
    print("✅ Catálogo Arroba procesado.")

def obtener_tasa_cambio():
    """Obtiene la tasa de cambio desde ConfiguracionGlobal o usa un valor por defecto"""
    config = ConfiguracionGlobal.objects.first()
    if config and hasattr(config, 'tasa_cambio_usd_mxn'):
        return float(config.tasa_cambio_usd_mxn)
    return 17.0  # valor por defecto

def actualizar_datos_desde_arroba(archivo_excel):
    tasa_cambio = obtener_tasa_cambio()
    print(f"🔄 Usando tasa de cambio {tasa_cambio}")

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
    
    def procesar_catalogo_arroba(ruta_archivo):
        print("✅ Procesando catálogo Arroba:", ruta_archivo)
