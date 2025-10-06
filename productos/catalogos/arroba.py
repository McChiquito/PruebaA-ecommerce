import pandas as pd
from django.db import transaction
from productos.models import Producto, Proveedor, ProveedorPrecio


def procesar_catalogo_arroba(ruta_archivo, proveedor):
    print(f"📥 Procesando catálogo Arroba: {ruta_archivo}")
    print(f"🔄 Configuración actual → Tasa: {proveedor.tasa_cambio_usd_mxn} | IVA: {proveedor.porcentaje_iva}% | Incluye IVA: {proveedor.incluye_iva}")

    try:
        df = pd.read_excel(ruta_archivo, header=4)
        df.columns = df.columns.str.strip().str.upper()
        print("📄 Columnas detectadas:", list(df.columns))

        productos_actualizados = 0

        with transaction.atomic():
            for _, fila in df.iterrows():
                sku = str(fila.get("CLAVE DE ARTÍCULO")).strip() if pd.notna(fila.get("CLAVE DE ARTÍCULO")) else None
                if not sku or sku == "-":
                    continue

                try:
                    producto = Producto.objects.get(sku=sku)
                except Producto.DoesNotExist:
                    print(f"❌ SKU no encontrado: {sku}")
                    continue

                # Obtener precio
                precio = None
                if pd.notna(fila.get("PROMOCION")) and float(fila.get("PROMOCION")) > 0:
                    precio = float(fila.get("PROMOCION"))
                elif pd.notna(fila.get("PRECIO")):
                    precio = float(fila.get("PRECIO"))

                if precio is None:
                    continue

                # Conversión de moneda
                moneda = str(fila.get("MONEDA")).strip().upper() if pd.notna(fila.get("MONEDA")) else "MXN"
                if moneda in ["USD", "DOLARES"]:
                    precio *= proveedor.tasa_cambio_usd_mxn

                # Aplicar IVA si no está incluido
                if not proveedor.incluye_iva:
                    precio *= (1 + proveedor.porcentaje_iva / 100)

                # Determinar stock
                stock = 0
                if "CEDIS" in df.columns and pd.notna(fila.get("CEDIS")):
                    try:
                        stock = int(fila.get("CEDIS"))
                    except ValueError:
                        stock = 0

                # Guardar o actualizar
                ProveedorPrecio.objects.update_or_create(
                    producto=producto,
                    proveedor=proveedor,
                    defaults={
                        "precio": round(precio, 2),
                        "stock": stock,
                    },
                )

                productos_actualizados += 1
                print(f"✅ {sku} → ${round(precio, 2)} MXN (IVA {'incluido' if proveedor.incluye_iva else 'aplicado'})")

        print(f"✅ Catálogo Arroba procesado correctamente ({productos_actualizados} productos actualizados).")

    except Exception as e:
        print(f"❌ Error general procesando catálogo Arroba: {e}")
