import pandas as pd
from productos.models import Producto, ConfiguracionGlobal
from django.db import transaction

config = ConfiguracionGlobal.objects.first()
tasa_cambio = float(config.tasa_cambio_usd_mxn) if config else 17.0


def actualizar_datos_desde_arroba(archivo_xlsx):
    try:
        df = pd.read_excel(archivo_xlsx, skiprows=4)  # Empieza desde fila 5
        columnas = df.columns.tolist()
        print("Columnas del archivo:", columnas)

        actualizados = 0
        errores = 0

        for index, row in df.iterrows():
            try:
                sku = str(row['Clave de Artículo']).strip()

                # --- Normalizamos la moneda ---
                moneda_raw = str(row.get('Moneda', 'MXN')).strip().upper()
                if 'DOLAR' in moneda_raw:
                    moneda = 'USD'
                elif 'PESO' in moneda_raw or 'MXN' in moneda_raw:
                    moneda = 'MXN'
                else:
                    moneda = 'MXN'

                precio_base = float(row.get('Precio', 0))
                promocion = row.get('Promocion', 0)

                if pd.isna(promocion):
                    promocion = 0
                try:
                    promocion = float(promocion)
                except:
                    promocion = 0

                # --- Lógica de precio ---
                if moneda == 'MXN':
                    precio_final = precio_base - promocion
                elif moneda == 'USD':
                    if promocion > 0:
                        precio_final = promocion * tasa_cambio
                    else:
                        precio_final = precio_base * tasa_cambio
                if precio_final <= 0:
                    print(f"[Precio inválido] SKU: {sku} - Precio calculado: {precio_final}")
                    errores += 1
                    continue

                with transaction.atomic():
                    producto = Producto.objects.get(sku=sku)
                    producto.precio = precio_final
                    producto.save()
                    print(f"[Actualizado] SKU: {sku} -> ${precio_final:.2f} ({moneda})")
                    actualizados += 1
                # --- logiica del Stock ---
                stock = int(row.get('CEDIS', 0))
                producto.stock = stock

            except Producto.DoesNotExist:
                print(f"[No encontrado] SKU no existe en DB: {sku}")
                errores += 1
            except Exception as e:
                print(f"[Error inesperado] SKU: {row.get('Clave de Artículo', 'Desconocido')} -> {str(e)}")
                errores += 1

        print(f"✅ Productos actualizados: {actualizados}")
        print(f"❌ Errores durante la actualización: {errores}")
        print("✅ Actualización finalizada sin errores críticos.")
        return {'actualizados': actualizados, 'errores': errores}

    except Exception as e:
        print(f"❌ Error general durante la carga del archivo: {str(e)}")
        return None
