# productos/admin.py
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Producto, Conversation, Categoria,Proveedor,TipoCambio, ChatMessage, ConfiguracionGlobal

admin.site.register(Proveedor)
admin.site.register(TipoCambio)

@admin.register(ConfiguracionGlobal)
class ConfiguracionGlobalAdmin(admin.ModelAdmin):
    list_display = ('id', 'tasa_cambio_usd_mxn')
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    search_fields = ('nombre',)
    prepopulated_fields = {'slug': ('nombre',)}
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'sku', 
        'nombre', 
        'categoria', 
        'precio_dolar', # Puedes mantener esta si quieres ver el precio en dólar también
        'inventario', 
        'activo', 
        'precio_mxn_display' # Esta es la clave para mostrar el precio en pesos
    )
    search_fields = ('sku', 'nombre', 'descripcion')
    list_filter = ('categoria', 'activo', 'proveedor')
    def precio_mxn_display(self, obj):
        # Asegura que se muestre un formato amigable para el usuario, puedes añadir moneda
        if obj.precio_mxn: # precio_mxn es tu propiedad calculada en models.py
            return f'${obj.precio_mxn:.2f} MXN'
        return '-'
    list_filter = (
        'activo',
        'categoria',
        "marca",
        )
    search_fields = (
        'nombre'
        'sku', 
        'descripcion', 
        'marca',
        )
    # Añade otros campos según necesites para tu Producto

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('get_identifier', 'user', 'session_key', 'created_at', 'updated_at', 'is_closed', 'view_chat_action')
    list_filter = ('is_closed', 'created_at', 'updated_at')
    search_fields = ('user__username', 'session_key')
    readonly_fields = ('created_at', 'updated_at')

    def get_identifier(self, obj):
        if obj.user:
            return f"Usuario: {obj.user.username}"
        elif obj.session_key:
            return f"Anónimo: {obj.session_key[:8]}..."
        return f"ID: {obj.id}"
    get_identifier.short_description = "Identificador"

    def view_chat_action(self, obj):
        # Genera la URL para tu panel de chat con el ID de la conversación
        # Asegúrate de que los nombres de las URLs en productos/urls.py son correctos
        url = reverse('productos:admin_chat_panel_detail', args=[obj.id])
        return format_html('<a class="button" href="{}">Ver Chat</a>', url)
    view_chat_action.short_description = "Acción de Chat"
    # view_chat_action.allow_tags = True # Esta línea es obsoleta en Django 2.0+ y no es necesaria

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender_is_admin', 'message_snippet', 'timestamp') # CAMBIADO: 'message' a 'message_snippet'
    list_filter = ('sender_is_admin', 'timestamp')
    search_fields = ('message', 'conversation__user__username', 'conversation__session_key') # Añadido búsqueda por conversación
    readonly_fields = ('conversation', 'sender_is_admin', 'message', 'timestamp') # CAMBIADO: 'raw_id_fields' a 'readonly_fields'

    def message_snippet(self, obj): # AÑADIDO: Método para mostrar un fragmento del mensaje
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_snippet.short_description = "Mensaje"

# admin.site.register(Producto) # REMOVIDO: Ya no es necesario con @admin.register(Producto)