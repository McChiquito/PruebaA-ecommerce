from productos.models import ConfiguracionGlobal

def get_tasa_dolar():
    """
    Obtiene la tasa de dólar desde ConfiguracionGlobal.
    Si no existe, usa un valor por defecto.
    """
    try:
        config = ConfiguracionGlobal.objects.get(nombre="tasa_dolar")
        return float(config.valor)  # ✅ se usa .valor, no .tasa_dolar
    except ConfiguracionGlobal.DoesNotExist:
        print("⚠️ No se encontró la tasa de dólar en ConfiguracionGlobal. Usando valor por defecto: 18.0")
        return 18.0
    except Exception as e:
        print(f"❌ Error al obtener la tasa de dólar: {e}")
        return 18.0


def convertir_a_mxn(precio_usd, tasa_dolar=None):
    """
    Convierte un precio en USD a MXN usando la tasa de cambio guardada.
    Si no se pasa tasa_dolar, se obtiene automáticamente.
    """
    if tasa_dolar is None:
        tasa_dolar = get_tasa_dolar()
    return round(precio_usd * tasa_dolar, 2)
