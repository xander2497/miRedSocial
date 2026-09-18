from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Conversation, Message
from .serializers import CreateMessageSerializer


class ConversacionSinDuplicadosTests(APITestCase):
    """
    Test de integración: si dos usuarios inician conversación entre sí,
    sin importar quién la inicia primero, siempre debe existir UNA SOLA
    conversación entre ambos (no una por cada sentido).

    ¿Por qué este test es útil?
    StartConversationAPIView (chat/api_views.py) busca la conversación
    en ambos sentidos antes de crear una nueva:

        Conversation.objects.filter(user1=me, user2=other).first()
        or
        Conversation.objects.filter(user1=other, user2=me).first()

    Si alguien simplificara esa línea a solo un sentido (un error fácil
    de cometer), se crearían conversaciones duplicadas y los mensajes
    se repartirían entre dos hilos distintos sin que el usuario entienda
    por qué "desaparecen" mensajes.
    """

    def setUp(self):
        self.ana = User.objects.create_user(username="ana", password="clave12345")
        self.luis = User.objects.create_user(username="luis", password="clave12345")

    def test_iniciar_conversacion_en_ambos_sentidos_no_duplica(self):
        # --- Paso 1: Ana inicia conversación con Luis ---
        self.client.force_authenticate(user=self.ana)
        url_ana_a_luis = reverse('chat_api:start_conversation', args=[self.luis.id])
        response1 = self.client.post(url_ana_a_luis)

        self.assertIn(response1.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        id_conversacion_1 = response1.data["id"]

        # --- Paso 2: Luis inicia conversación con Ana (orden invertido) ---
        self.client.force_authenticate(user=self.luis)
        url_luis_a_ana = reverse('chat_api:start_conversation', args=[self.ana.id])
        response2 = self.client.post(url_luis_a_ana)

        id_conversacion_2 = response2.data["id"]

        # --- Verificaciones ---
        # Debe ser la MISMA conversación en ambos casos (mismo id)
        self.assertEqual(id_conversacion_1, id_conversacion_2)

        # Y en la base de datos solo debe existir UNA fila, no dos
        self.assertEqual(Conversation.objects.count(), 1)


class NoAutoChatTests(APITestCase):
    """
    Test de integración: un usuario no puede iniciar una conversación
    consigo mismo.

    StartConversationAPIView valida `if me.id == user_id: return 400`.
    Este test confirma que esa validación sigue activa.
    """

    def setUp(self):
        self.ana = User.objects.create_user(username="ana", password="clave12345")
        self.client.force_authenticate(user=self.ana)

    def test_no_se_puede_iniciar_chat_con_uno_mismo(self):
        url = reverse('chat_api:start_conversation', args=[self.ana.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Tampoco debe haberse creado ninguna conversación "fantasma"
        self.assertEqual(Conversation.objects.count(), 0)


class AislamientoConversacionesAjenasTests(APITestCase):
    """
    Test de seguridad (el más importante del proyecto): un usuario que
    NO participa en una conversación no debe poder leer sus mensajes
    ni enviar mensajes nuevos, aunque adivine el id de la conversación.

    ConversationsMessagesAPIView y SendMessageAPIView validan:
        if request.user not in [convo.user1, convo.user2]:
            return 403
    """

    def setUp(self):
        self.ana = User.objects.create_user(username="ana", password="clave12345")
        self.luis = User.objects.create_user(username="luis", password="clave12345")
        self.pedro = User.objects.create_user(username="pedro", password="clave12345")

        # Conversación EXISTENTE entre ana y luis (pedro no participa)
        self.conversacion = Conversation.objects.create(user1=self.ana, user2=self.luis)
        Message.objects.create(
            conversation=self.conversacion,
            sender=self.ana,
            content="Hola Luis, este mensaje es privado",
        )

        # Autenticamos como "pedro", un tercero ajeno a esta conversación
        self.client.force_authenticate(user=self.pedro)

    def test_no_puede_ver_mensajes_de_conversacion_ajena(self):
        url = reverse('chat_api:conversations_messages', args=[self.conversacion.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_no_puede_enviar_mensajes_a_conversacion_ajena(self):
        url = reverse('chat_api:send_message', args=[self.conversacion.id])
        response = self.client.post(url, {"content": "Mensaje de un intruso"})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Y ese mensaje NO debe haber quedado guardado en la base de datos
        self.assertEqual(
            Message.objects.filter(content="Mensaje de un intruso").count(), 0
        )


class MensajeVacioRechazadoTests(APITestCase):
    """
    Test unitario (no de integración): prueba directamente la clase
    CreateMessageSerializer, sin pasar por el cliente HTTP ni por la
    base de datos. Es el test más rápido de correr de todos.

    CreateMessageSerializer.validate_content() hace:
        if not value.strip():
            raise serializers.ValidationError(...)

    Es decir, un mensaje vacío o de solo espacios debe ser inválido.
    """

    def test_contenido_vacio_es_invalido(self):
        serializer = CreateMessageSerializer(data={"content": ""})

        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)

    def test_contenido_solo_espacios_es_invalido(self):
        serializer = CreateMessageSerializer(data={"content": "     "})

        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)

    def test_contenido_valido_es_aceptado(self):
        serializer = CreateMessageSerializer(data={"content": "Hola, cómo estás!"})

        self.assertTrue(serializer.is_valid())
