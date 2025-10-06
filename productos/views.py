# productos/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import F, DecimalField, ExpressionWrapper, Case, When
from .models import Producto, Conversation, ChatMessage, ProveedorPrecio, ConfiguracionGlobal
import pandas as pd
from django.core.management import call_command
import os
from django.conf import settings
from django.http import JsonResponse
from rest_framework import generics
from .serializers import ProductoSerializer
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
import json
from django.utils import timezone
from productos.forms import ArrobaCatalogForm, ProceCatalogForm, TechsmartCatalogForm
from productos.catalogos.arroba import procesar_catalogo_arroba
from productos.catalogos.proce import procesar_catalogo_proce
from productos.catalogos.techsmart import procesar_catalogo_techsmart

from django.urls import reverse
from core.utils import get_tasa_dolar

tasa = get_tasa_dolar()

def admin_dashboard(request):
    # Instanciar los formularios vacíos
    form_arroba = ArrobaCatalogForm()
    form_proce = ProceCatalogForm()
    form_techsmart = TechsmartCatalogForm()

    if request.method == 'POST':
        if 'arroba_catalog' in request.FILES:
            file = request.FILES['arroba_catalog']
            path = default_storage.save(f'temp/{file.name}', file)
            full_path = os.path.join(settings.MEDIA_ROOT, path)
            procesar_catalogo_arroba(full_path)

        elif 'proce_catalog' in request.FILES:
            file = request.FILES['proce_catalog']
            path = default_storage.save(f'temp/{file.name}', file)
            full_path = os.path.join(settings.MEDIA_ROOT, path)
            procesar_catalogo_proce(full_path)

        elif 'techsmart_catalog' in request.FILES:
            file = request.FILES['techsmart_catalog']
            path = default_storage.save(f'temp/{file.name}', file)
            full_path = os.path.join(settings.MEDIA_ROOT, path)
            procesar_catalogo_techsmart(full_path)

    context = {
        'form_arroba': form_arroba,
        'form_proce': form_proce,
        'form_techsmart': form_techsmart,
    }

    return render(request, 'productos/admin_dashboard.html')
  
def vista_catalogo(request):
    # Obtener todos los productos
    productos = Producto.objects.all()

    # Estructura: lista de diccionarios que agrupan productos y sus precios por proveedor
    productos_con_precios = []
    for producto in productos:
        precios = ProveedorPrecio.objects.filter(producto=producto)
        productos_con_precios.append({
            'producto': producto,
            'precios': list(precios.values('proveedor__nombre', 'precio_mxn', 'stock'))
        })

    context = {
        'productos_con_precios': productos_con_precios,
        'productos': productos,
    }

    return render(request, 'index.html', context)

# --- VISTA PARA LA PÁGINA DE INICIO ---
def inicio(request):
    return render(request, 'productos/index.html')


@login_required
@user_passes_test(lambda u: u.is_staff)
def upload_catalogs_view(request):
    """
    Procesa la carga de catálogos desde el dashboard de administración.
    """
    if request.method == 'POST':
        archivos = request.FILES
        base_path = os.path.join(settings.MEDIA_ROOT, 'catalogos_subidos')
        os.makedirs(base_path, exist_ok=True)

        from productos.models import Proveedor

        # --- Catálogo Arroba ---
        if 'catalogo_arroba' in archivos:
            archivo = archivos['catalogo_arroba']
            ruta = os.path.join(base_path, archivo.name)
            with open(ruta, 'wb+') as dest:
                for chunk in archivo.chunks():
                    dest.write(chunk)

            proveedor = Proveedor.objects.filter(nombre__iexact="Arroba").first()
            if not proveedor:
                messages.error(request, "⚠️ No se encontró el proveedor 'Arroba'.")
            else:
                try:
                    procesar_catalogo_arroba(ruta, proveedor)
                    messages.success(request, f'✅ Catálogo de Arroba procesado correctamente.')
                except Exception as e:
                    messages.error(request, f'❌ Error procesando catálogo de Arroba: {e}')

        # --- Catálogo Proce ---
        if 'catalogo_proce' in archivos:
            archivo = archivos['catalogo_proce']
            ruta = os.path.join(base_path, archivo.name)
            with open(ruta, 'wb+') as dest:
                for chunk in archivo.chunks():
                    dest.write(chunk)

            proveedor = Proveedor.objects.filter(nombre__iexact="Proce").first()
            if not proveedor:
                messages.error(request, "⚠️ No se encontró el proveedor 'Proce'.")
            else:
                try:
                    procesar_catalogo_proce(ruta, proveedor)
                    messages.success(request, f'✅ Catálogo de Proce procesado correctamente.')
                except Exception as e:
                    messages.error(request, f'❌ Error procesando catálogo de Proce: {e}')

        # --- Catálogo Techsmart ---
        if 'catalogo_techsmart' in archivos:
            archivo = archivos['catalogo_techsmart']
            ruta = os.path.join(base_path, archivo.name)
            with open(ruta, 'wb+') as dest:
                for chunk in archivo.chunks():
                    dest.write(chunk)

            proveedor = Proveedor.objects.filter(nombre__iexact="Techsmart").first()
            if not proveedor:
                messages.error(request, "⚠️ No se encontró el proveedor 'Techsmart'.")
            else:
                try:
                    procesar_catalogo_techsmart(ruta, proveedor)
                    messages.success(request, f'✅ Catálogo de Techsmart procesado correctamente.')
                except Exception as e:
                    messages.error(request, f'❌ Error procesando catálogo de Techsmart: {e}')

        return redirect('productos:admin_dashboard')

    return render(request, 'productos/admin_dashboard.html')

def guardar_archivo_excel(excel_file):
    file_path = os.path.join(settings.MEDIA_ROOT, 'excel_files', excel_file.name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'wb+') as destination:
        for chunk in excel_file.chunks():
            destination.write(chunk)
    return file_path


# --- VISTA PARA LA PÁGINA DE CARGA DE ARCHIVO EXCEL ---
@login_required
@user_passes_test(lambda u: u.is_staff)
def upload_excel_view(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']

            # 1. Guarda el archivo Excel en tu carpeta excel_files (o MEDIA_ROOT)
            file_path = os.path.join(settings.MEDIA_ROOT, 'excel_files', excel_file.name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            try:
                with open(file_path, 'wb+') as destination:
                    for chunk in excel_file.chunks():
                        destination.write(chunk)
                messages.success(request, f'Archivo "{excel_file.name}" subido exitosamente.')

                # 2. Llama al comando de importación/actualización
                try:
                    call_command('update_productos_from_excel', file_path)
                    messages.success(request, 'Productos actualizados desde Excel correctamente.')
                except Exception as e:
                    messages.error(request, f'Error al actualizar productos desde Excel: {e}')
                    if os.path.exists(file_path):
                        os.remove(file_path)

                return redirect(reverse('productos:upload_excel_page'))

            except Exception as e:
                messages.error(request, f'Error al guardar el archivo: {e}')
                return render(request, 'productos/upload_excel.html', {'form': form})
        else:
            messages.error(request, 'El formulario no es válido. Por favor, revisa el archivo.')
            return render(request, 'productos/upload_excel.html', {'form': form})
    else:
        form = ExcelUploadForm()
    return render(request, 'productos/upload_excel.html', {'form': form})


# --- VISTA PARA EL DASHBOARD DE ADMINISTRACIÓN PERSONALIZADO ---
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard_view(request):
    return render(request, 'productos/admin_dashboard.html')

def catalogo_view(request):
    productos = Producto.objects.all().prefetch_related('precioproveedor_set', 'categoria')
    productos_con_precios = []

    for producto in productos:
        precios = (
            ProveedorPrecio.objects
            .filter(producto=producto)
            .values('proveedor__nombre', 'precio_mxn', 'stock')
        )
        productos_con_precios.append({
            'producto': producto,
            'precios': precios
        })

    context = {'productos_con_precios': productos_con_precios}
    return render(request, 'index.html', context)
# Esta vista renderiza tu plantilla HTML (ej. para la página principal de productos)
# --- VISTA PARA LA PÁGINA PRINCIPAL DE PRODUCTOS ---
def index(request):
    from productos.models import Producto, ProveedorPrecio
    from core.utils import get_tasa_dolar

    productos = Producto.objects.all()
    tasa_cambio = get_tasa_dolar()

    productos_con_precios = []

    for producto in productos:
        # Obtener todos los precios de los proveedores asociados
        precios_proveedores = ProveedorPrecio.objects.filter(producto=producto).select_related('proveedor')

        precios_convertidos = []
        for p in precios_proveedores:
            tasa = p.proveedor.tasa_cambio_usd_mxn or tasa_cambio
            precio_final = p.precio

            # Si la moneda es USD, convertir a MXN
            if p.moneda == 'USD':
                precio_final *= tasa

            # Si el proveedor NO incluye IVA, aplicar el IVA correspondiente
            if not p.proveedor.incluye_iva:
                precio_final *= (1 + (p.proveedor.porcentaje_iva / 100))

            precios_convertidos.append({
                'proveedor': p.proveedor.nombre,
                'precio_final': round(precio_final, 2),
                'stock': p.stock,
                'moneda': 'MXN'
            })

        # Mostrar información dependiendo del tipo de usuario
        if request.user.is_authenticated and request.user.is_staff:
            productos_con_precios.append({
                'producto': producto,
                'precios': precios_convertidos
            })
        else:
            # Mostrar el menor precio
            mejor_precio = min([p['precio_final'] for p in precios_convertidos], default=None)
            productos_con_precios.append({
                'producto': producto,
                'precio_mas_bajo': mejor_precio,
                'moneda': 'MXN'
            })

    return render(request, 'productos/index.html', {'productos_con_precios': productos_con_precios})

# Tu vista de la API (si usas Django REST Framework)
class ProductoAPIView(generics.ListAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

# --- VISTA PARA EL PANEL DE CHAT DEL ADMINISTRADOR ---
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_chat_panel(request, conversation_id=None):
    conversations = Conversation.objects.all().order_by('-updated_at')

    current_conversation = None
    chat_messages = []
    if conversation_id:
        current_conversation = get_object_or_404(Conversation, id=conversation_id)
        chat_messages = ChatMessage.objects.filter(conversation=current_conversation).order_by('timestamp')

    context = {
        'conversations': conversations,
        'current_conversation': current_conversation,
        'chat_messages': chat_messages
    }
    return render(request, 'productos/admin_chat_panel.html', context)

def vista_principal(request):
    productos = Producto.objects.all().prefetch_related("preciosproveedor_set", "categoria")

    productos_con_precios = []
    for producto in productos:
        precios = (
            ProveedorPrecio.objects.filter(producto=producto)
            .values("proveedor__nombre", "precio_mxn", "stock")
        )
        productos_con_precios.append({
            "producto": producto,
            "precios": list(precios)
        })

    context = {
        "productos_con_precios": productos_con_precios
    }
    return render(request, "index.html", context)

@csrf_exempt
@require_POST
def start_chat_view(request):
    try:
        data = json.loads(request.body)
        user_name = data.get('user_name')
        initial_message_text = data.get('initial_message')
        session_key_from_js = data.get('session_key')

        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key

        if not session_key and session_key_from_js:
            session_key = session_key_from_js

        if not session_key and not request.user.is_authenticated:
            raise ValueError("No se pudo establecer la clave de sesión para un usuario anónimo.")

        user = request.user if request.user.is_authenticated else None

        if user:
            conversation, created = Conversation.objects.get_or_create(user=user, defaults={'is_closed': False})
        else:
            conversation, created = Conversation.objects.get_or_create(session_key=session_key, defaults={'is_closed': False})

        if conversation.is_closed:
            conversation.is_closed = False
            conversation.save()

        user_display_name = user.username if user else user_name if user_name else "Anónimo"
        ChatMessage.objects.create(
            conversation=conversation,
            sender_is_admin=False,
            message=f"Nombre: {user_display_name}\nConsulta: {initial_message_text}"
        )

        return JsonResponse({'conversation_id': conversation.id})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)


@login_required
@user_passes_test(lambda u: u.is_staff)
@csrf_exempt
@require_POST
def close_conversation_api(request, conversation_id):
    try:
        conversation = get_object_or_404(Conversation, id=conversation_id)
        conversation.is_closed = True
        conversation.save()
        return JsonResponse({'status': 'success', 'message': f'Conversación {conversation_id} cerrada.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
# ==========================================================
# API: Productos en formato JSON (para el catálogo principal)
# ==========================================================

def api_productos(request):
    productos = Producto.objects.all()
    data = []

    for p in productos:
        # Obtener los precios por proveedor
        precios_proveedor = []
        precios = ProveedorPrecio.objects.filter(producto=p)
        for pp in precios:
            precios_proveedor.append({
                "proveedor": pp.proveedor.nombre,
                "precio": float(pp.precio) if pp.precio else None,
                "stock": pp.stock if pp.stock is not None else 0,
            })

        # Calcular el precio mínimo (por si quieres mostrar el más barato)
        precio_min = min(
            [pp["precio"] for pp in precios_proveedor if pp["precio"] is not None],
            default=None
        )

        data.append({
            "id": p.id,
            "sku": p.sku,
            "nombre": getattr(p, "descripcion", "Sin nombre"),
            "descripcion": getattr(p, "descripcion", ""),
            "categoria_nombre": p.categoria.nombre if hasattr(p, "categoria") and p.categoria else "Sin categoría",
            "imagen": p.imagen.url if hasattr(p, "imagen") and p.imagen else "",
            "inventario": getattr(p, "inventario", 0),
            "garantia": getattr(p, "garantia", None),
            "precios_proveedor": precios_proveedor,  # 🔥 aquí van los detalles
            "precio_minimo": precio_min,  # 🔥 precio más barato
        })

    return JsonResponse(data, safe=False)
    productos = Producto.objects.all()
    data = []

    for p in productos:
        data.append({
            'id': p.id,
            'sku': p.sku,
            'nombre': getattr(p, 'descripcion', 'Sin nombre'),  # ✅ corregido
            'descripcion': getattr(p, 'descripcion', ''),
            'precio_mxn': float(p.precio_mxn) if hasattr(p, 'precio_mxn') else 0,
            'categoria_nombre': p.categoria.nombre if hasattr(p, 'categoria') and p.categoria else 'Sin categoría',
            'imagen': p.imagen.url if hasattr(p, 'imagen') and p.imagen else '',
            'inventario': getattr(p, 'inventario', 0),
            'garantia_meses': getattr(p, 'garantia', None),
        })

    return JsonResponse(data, safe=False)

    productos = Producto.objects.all().prefetch_related("proveedorprecio_set")

    data = []
    for producto in productos:
        precios = []
        for precio in producto.proveedorprecio_set.all():
            precios.append({
                "proveedor": precio.proveedor.nombre,
                "precio": round(precio.precio, 2),
                "stock": precio.stock,
            })

        data.append({
            "sku": producto.sku,
            "descripcion": producto.descripcion,
            "garantia": producto.garantia,
            "condicion": producto.condicion,
            "categoria": producto.categoria.nombre if producto.categoria else "",
            "precios": precios,
        })

    return JsonResponse({"productos": data})
    productos = Producto.objects.select_related('categoria').all()

    data = []
    for p in productos:
        data.append({
            "id": p.id,
            "sku": p.sku,
            "nombre": p.nombre,
            "descripcion": p.descripcion,
            "categoria_nombre": p.categoria.nombre if p.categoria else "",
            "precio_mxn": p.precio_dolar,  # o p.precio_mxn si lo tienes
            "inventario": p.stock,  # o el campo que uses
            "imagen": p.imagen.url if p.imagen else "",
            "garantia": p.garantia,
        })

    return JsonResponse(data, safe=False)