# productos/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Producto, Conversation, ChatMessage
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
from .forms import ExcelUploadForm, CatalogoProveedorForm
from django.urls import reverse
from .management.commands.actualizar_arroba import procesar_excel_catalogo
# --- VISTA PARA SUBIR CATÁLOGO DE PROVEEDOR ---
@login_required
def subir_catalogo_dashboard(request):
    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        try:
            procesar_excel_catalogo(archivo)  # Tu lógica para actualizar productos
            messages.success(request, 'Catálogo actualizado correctamente.')
        except Exception as e:
            messages.error(request, f'Error al procesar el archivo: {e}')
        return redirect('productos:admin_dashboard')  # Redirige al panel después de subir
    return redirect('productos:admin_dashboard')

def subir_catalogo(request):
    if request.method == 'POST':
        form = CatalogoProveedorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Catálogo subido exitosamente.')
            return redirect('productos:subir_catalogo')
        else:
            messages.error(request, 'Error al subir el catálogo. Por favor, revisa el formulario.')
    else:
        form = CatalogoProveedorForm()
    return render(request, 'productos/subir_catalogo.html', {'form': form})
# --- VISTA PARA LA PÁGINA DE INICIO ---
def inicio(request):
    return render(request, 'index.html')
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
    productos = Producto.objects.filter(activo=True).order_by('nombre')
    context = {
        'productos': productos
    }
    return render(request, 'productos/index.html', context)

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