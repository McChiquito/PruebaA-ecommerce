import tabula
from productos.models import Producto, ConfiguracionGlobal

def obtener_tasa_cambio():
    config = ConfiguracionGlobal.objects.first()
    return float(config.tasa_cambio_usd_mxn) if config and hasattr(config, 'tasa_cambio_usd_mxn') else 17.0

def actualizar_datos_desde_techsmart(archivo_pdf):
    tasa_cambio = obtener_tasa_cambio()
    print(f"✅ Tasa de cambio aplicada (Techsmart): {tasa_cambio}")

    tablas = tabula.read_pdf(archivo_pdf, pages='all', multiple_tables=True)

    for tabla in tablas:
        for _, row in tabla.iterrows():
            sku = str(row.get("Modelo")).strip() if row.get("Modelo") else None
            precio_raw = row.get("Precio c/Desc.")
            moneda = row.get("Moneda")
            if not sku or precio_raw is None:
                continue

            try:
                producto = Producto.objects.get(sku=sku)

                if moneda == "USD":
                    precio_final = float(precio_raw) * tasa_cambio
                else:
                    precio_final = float(precio_raw)

                producto.precio_techsmart = round(precio_final, 2)
                producto.save()
                print(f"✔️ Producto actualizado (Techsmart): {sku}")
            except Producto.DoesNotExist:
                print(f"❌ SKU no encontrado (Techsmart): {sku}")
