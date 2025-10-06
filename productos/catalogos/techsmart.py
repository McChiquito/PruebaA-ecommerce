import os
import re
import pdfplumber
from productos.models import Producto, ProveedorPrecio


def procesar_catalogo_techsmart(ruta_archivo, proveedor):
    print(f"📥 Procesando catálogo Techsmart: {ruta_archivo}")
    print(f"🔄 Configuración actual → Tasa: {proveedor.tasa_cambio_usd_mxn} | IVA: {proveedor.porcentaje_iva}% | Incluye IVA: {proveedor.incluye_iva}")

    if not os.path.exists(ruta_archivo):
        print(f"❌ El archivo {ruta_archivo} no existe.")
        return

    productos_actualizados = 0

    with pdfplumber.open(ruta_archivo) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if not texto:
                continue

            for linea in texto.split("\n"):
                match = re.search(r"(?P<sku>[A-Z0-9\-]+).*?\$\s*(?P<precio>\d+(?:\.\d+)?).*?(?P<moneda>USD|MXN)", linea)
                if not match:
                    continue

                sku = match.group("sku").strip()
                precio = float(match.group("precio"))
                moneda = match.group("moneda").strip()

                try:
                    producto = Producto.objects.get(sku=sku)
                except Producto.DoesNotExist:
                    print(f"⚠️ SKU no encontrado en base: {sku}")
                    continue

                # Conversión de moneda
                if moneda == "USD":
                    precio_mxn = precio * proveedor.tasa_cambio_usd_mxn
                else:
                    precio_mxn = precio

                # Aplicar IVA si no está incluido
                if not proveedor.incluye_iva:
                    precio_mxn *= (1 + proveedor.porcentaje_iva / 100)

                ProveedorPrecio.objects.update_or_create(
                    producto=producto,
                    proveedor=proveedor,
                    defaults={
                        "precio": round(precio_mxn, 2),
                        "moneda": "MXN",
                        "stock": 5,
                    },
                )

                productos_actualizados += 1
                print(f"✅ {sku} → ${round(precio_mxn, 2)} MXN (IVA {'incluido' if proveedor.incluye_iva else 'aplicado'})")

    print(f"✅ Catálogo Techsmart procesado correctamente ({productos_actualizados} productos actualizados).")
