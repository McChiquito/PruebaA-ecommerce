from productos.models import ConfiguracionGlobal

def get_tasa_dolar():
    """
    Obtiene la tasa de conversión USD → MXN desde la configuración global.
    """
    try:
        config = ConfiguracionGlobal.objects.first()
        if config and config.tasa_dolar:
            return config.tasa_dolar
        else:
            print("⚠️ No se encontró la tasa de dólar en ConfiguracionGlobal. Usando valor por defecto: 18.0")
            return 18.0
    except Exception as e:
        print(f"❌ Error al obtener la tasa de dólar: {e}")
        return 18.0


def convertir_a_mxn(precio_usd, tasa):
    """
    Convierte un precio en dólares a pesos mexicanos usando la tasa dada.
    """
    try:
        return round(precio_usd * tasa, 2)
    except Exception as e:
        print(f"❌ Error al convertir USD a MXN: {e}")
        return precio_usd  # Regresa el original como fallback
