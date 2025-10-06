import pandas as pd
from productos.models import Producto, ProveedorPrecio

def procesar_catalogo_proce(ruta_archivo, proveedor):
    print(f"\n📥 Procesando catálogo Proce: {ruta_archivo}")
    try:
        # Leer el archivo Excel
        df = pd.read_excel(ruta_archivo, header=2)
        print(f"📄 Columnas detectadas: {list(df.columns)}")

        # Normalizar nombres de columnas
        df.columns = [str(c).strip().upper() for c in df.columns]

        # Verificar que existan las columnas clave
        columnas_necesarias = ['SKU', 'PRECIOS PESOS NETOS', 'INVENTARIO']
        for col in columnas_necesarias:
            if col not in df.columns:
                raise ValueError(f"❌ Falta la columna '{col}' en el catálogo Proce")

        # Configuración del proveedor
        tasa = float(proveedor.tasa_cambio_usd_mxn)
        incluye_iva = proveedor.incluye_iva
        iva = float(proveedor.porcentaje_iva)
        print(f"🔄 Configuración actual → Tasa: {tasa} | IVA: {iva}% | Incluye IVA: {incluye_iva}")

        actualizados = 0
        for _, fila in df.iterrows():
            sku = str(fila['SKU']).strip()
            precio_bruto = fila.get('PRECIOS PESOS NETOS')
            stock = fila.get('INVENTARIO', 0)

            # Validar precio
            if pd.isna(precio_bruto) or not isinstance(precio_bruto, (int, float)):
                print(f"⚠️ Sin precio válido para SKU {sku}")
                continue

            # Si el precio ya viene en pesos, no aplicar tasa
            precio_mxn = float(precio_bruto)

            # Si el proveedor NO incluye IVA → aplicarlo
            if not incluye_iva:
                precio_final = precio_mxn * (1 + iva / 100)
            else:
                precio_final = precio_mxn

            # Buscar producto existente
            producto = Producto.objects.filter(sku=sku).first()
            if not producto:
                print(f"❌ SKU no encontrado en base: {sku}")
                continue

            # Actualizar o crear registro de precio por proveedor
            proveedor_precio, _ = ProveedorPrecio.objects.update_or_create(
                producto=producto,
                proveedor=proveedor,
                defaults={
                    'precio': round(precio_final, 2),
                    'stock': int(stock) if not pd.isna(stock) else 0,
                }
            )

            # 🔍 Log detallado
            print(f"🔍 SKU {sku} | Precio leído: {precio_mxn:.2f} | Final aplicado: {precio_final:.2f} | Stock: {stock}")
            actualizados += 1

        print(f"✅ Catálogo Proce procesado correctamente ({actualizados} productos actualizados).")

    except Exception as e:
        print(f"❌ Error procesando catálogo de Proce: {e}")
