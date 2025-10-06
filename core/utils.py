# ============================================
# core/utils.py — Utilidades globales del sistema
# ============================================

from productos.models import ConfiguracionGlobal, Proveedor

# ============================================================
# 0️⃣ Obtener IVA específico por proveedor
# ============================================================
def obtener_iva_proveedor(nombre_proveedor):
    """
    Devuelve el IVA específico del proveedor, o el valor por defecto (16%)
    """
    try:
        proveedor = Proveedor.objects.get(nombre__iexact=nombre_proveedor)
        if hasattr(proveedor, 'iva') and proveedor.iva is not None:
            return proveedor.iva
        else:
            return 0.16  # valor por defecto
    except Proveedor.DoesNotExist:
        return 0.16

# ============================================================
# 1️⃣ Obtener tasa global de dólar desde ConfiguracionGlobal
# ============================================================
def get_tasa_dolar():
    """
    Obtiene la tasa global de dólar (USD → MXN) desde el modelo ConfiguracionGlobal.
    Si no existe, devuelve un valor por defecto (18.0).
    """
    try:
        config = ConfiguracionGlobal.objects.first()
        if config:
            return float(config.tasa_cambio_usd_mxn)
        else:
            print("⚠️ No se encontró registro de ConfiguracionGlobal. Usando valor por defecto: 18.0")
            return 18.0
    except Exception as e:
        print(f"❌ Error al obtener la tasa de dólar: {e}")
        return 18.0


# ============================================================
# 2️⃣ Conversión de precios de USD a MXN
# ============================================================
def convertir_a_mxn(precio_usd, tasa_dolar=None):
    """
    Convierte un precio expresado en USD a MXN, usando la tasa proporcionada.
    Si no se pasa una tasa, usa la función get_tasa_dolar().
    """
    if tasa_dolar is None:
        tasa_dolar = get_tasa_dolar()
    try:
        return round(float(precio_usd) * float(tasa_dolar), 2)
    except Exception as e:
        print(f"⚠️ Error al convertir precio: {e}")
        return float(precio_usd)


# ============================================================
# 3️⃣ Obtener tasa específica por proveedor
# ============================================================
def obtener_tasa_proveedor(nombre_proveedor):
    """
    Devuelve la tasa de cambio USD→MXN específica de un proveedor.
    Si el proveedor no existe o no tiene tasa configurada,
    usa la tasa global o el valor por defecto (18.0).
    """
    try:
        proveedor = Proveedor.objects.get(nombre=nombre_proveedor)
        if hasattr(proveedor, "tasa_cambio_usd_mxn"):
            return float(proveedor.tasa_cambio_usd_mxn)
        else:
            print(f"⚠️ El proveedor {nombre_proveedor} no tiene campo de tasa_cambio_usd_mxn. Usando global.")
            return get_tasa_dolar()
    except Proveedor.DoesNotExist:
        print(f"⚠️ Proveedor '{nombre_proveedor}' no encontrado. Usando tasa global.")
        return get_tasa_dolar()
    except Exception as e:
        print(f"❌ Error al obtener tasa de proveedor '{nombre_proveedor}': {e}")
        return 18.0
