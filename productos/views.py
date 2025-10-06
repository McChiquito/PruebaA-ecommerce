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

    return render(request, 'admin_dashboard.html', context)
  
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
    return render(request, 'index.html')

@login_required
@user_passes_test(lambda u: u.is_staff)
def upload_catalogs_view(request):
    arroba_form = ExcelUploadForm(prefix='arroba')
    proce_form = ExcelUploadForm(prefix='proce')
    techsmart_form = ExcelUploadForm(prefix='techsmart')  # ✅ reutilizamos el mismo form, ya que solo valida archivo

    if request.method == 'POST':
        if 'arroba-submit' in request.POST:
            arroba_form = ExcelUploadForm(request.POST, request.FILES, prefix='arroba')
            if arroba_form.is_valid():
                archivo = arroba_form.cleaned_data['excel_file']
                ruta = guardar_archivo_excel(archivo)
                try:
                    call_command('actualizar_arroba', file=ruta)
                    messages.success(request, 'Catálogo de Arroba actualizado correctamente.')
                except Exception as e:
                    messages.error(request, f'Error con catálogo Arroba: {e}')

        elif 'proce-submit' in request.POST:
            proce_form = ExcelUploadForm(request.POST, request.FILES, prefix='proce')
            if proce_form.is_valid():
                archivo = proce_form.cleaned_data['excel_file']
                ruta = guardar_archivo_excel(archivo)
                try:
                    call_command('actualizar_proce', file=ruta)
                    messages.success(request, 'Catálogo de Proce actualizado correctamente.')
                except Exception as e:
                    messages.error(request, f'Error con catálogo Proce: {e}')

        elif 'techsmart-submit' in request.POST:
            techsmart_form = ExcelUploadForm(request.POST, request.FILES, prefix='techsmart')
            if techsmart_form.is_valid():
                archivo = techsmart_form.cleaned_data['excel_file']
                ruta = guardar_archivo_excel(archivo)
                try:
                    call_command('actualizar_techsmart', file=ruta)
                    messages.success(request, 'Catálogo de Techsmart (PDF) procesado correctamente.')
                except Exception as e:
                    messages.error(request, f'Error con catálogo Techsmart: {e}')

    context = {
        'arroba_form': arroba_form,
        'proce_form': proce_form,
        'techsmart_form': techsmart_form,
    }
    return render(request, 'productos/upload_catalogs.html', context)


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


# Esta vista renderiza tu plantilla HTML (ej. para la página principal de productos)
def index(request):
    productos = Producto.objects.all()
    tasa_cambio = get_tasa_dolar()


    productos_con_precios = []
    for producto in productos:
        proveedores = (producto.proveedorprecio_set
            .annotate(
                precio_mxn=Case(
                    When(moneda='USD', then=ExpressionWrapper(F('precio') * tasa_cambio, output_field=DecimalField())),
                    default=F('precio'),
                    output_field=DecimalField()
                )
            )
        )

        if request.user.is_authenticated and request.user.is_staff:
            # Admin: todos los proveedores
            precios = proveedores.values('proveedor__nombre', 'precio', 'moneda', 'stock')
            productos_con_precios.append({
                'producto': producto,
                'precios': precios
            })
        else:
            # Visitante: solo el menor precio convertido a MXN
            mejor = proveedores.order_by('precio_mxn').first()
            productos_con_precios.append({
                'producto': producto,
                'precio_mas_bajo': mejor.precio_mxn if mejor else None,
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