# productos/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Conversation, ChatMessage
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from django.utils import timezone # Importa timezone para la hora actual

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # El room_name ahora se usará como el ID de la conversación
        # Acceder a 'conversation_id' porque así está definido en routing.py
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'

        # Unir al grupo de sala
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Dejar el grupo de sala
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Recibir mensaje de WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_is_admin = text_data_json.get('sender_is_admin', False)

        # Guarda el mensaje en la base de datos
        # Ya no se pasa user_id o session_key aquí, ya que la conversación ya debería existir o ser manejada al inicio.
        await self.save_message(message, sender_is_admin, self.conversation_id)

        # Enviar mensaje al grupo de sala
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'is_admin': sender_is_admin,
                'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S') # Enviar la hora para el frontend
            }
        )

    # Recibir mensaje del grupo de sala
    async def chat_message(self, event):
        message = event['message']
        is_admin = event['is_admin']
        timestamp = event['timestamp']

        # Enviar mensaje a WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'is_admin': is_admin,
            'timestamp': timestamp
        }))

    @sync_to_async
    def save_message(self, message, sender_is_admin, conversation_id):
        # Asumiendo que la conversación con 'conversation_id' ya existe.
        # Si la conversación no existe al intentar guardar, esto generará un error.
        # La lógica para crear una nueva conversación (ya sea por usuario anónimo o registrado)
        # se manejará en el frontend o en una vista Django antes de iniciar el chat.
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            ChatMessage.objects.create(
                conversation=conversation,
                sender_is_admin=sender_is_admin,
                message=message
            )
            conversation.updated_at = timezone.now() # Actualiza la hora de la última actividad
            conversation.save()
        except Conversation.DoesNotExist:
            print(f"Error: Conversation with ID {conversation_id} does not exist. Message not saved.")
            # Aquí podrías añadir una lógica para notificar al cliente o cerrar la conexión.