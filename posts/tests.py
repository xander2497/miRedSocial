from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Post


class MisPostsAislamientoTests(APITestCase):
    """
    Test de integración: el endpoint "mis posts" (/api/posts/my/) debe
    devolver ÚNICAMENTE los posts del usuario que está autenticado,
    aunque existan posts de otros usuarios en la base de datos.

    ¿Por qué este test es útil?
    MyPostsAPIView (posts/api_views.py) filtra así:
        Post.objects.filter(author=request.user)

    Si alguien cambia ese filtro por accidente (por ejemplo, lo copia
    y pega de FeedPostsAPIView, que sí trae TODOS los posts), un
    usuario empezaría a ver posts que no le pertenecen en la sección
    "mis posts". Este test protege justo esa regla.
    """

    def setUp(self):
        # setUp() se ejecuta automáticamente ANTES de cada test de esta clase.
        # Aquí preparamos los datos que todos los tests de abajo necesitan.

        # Creamos dos usuarios distintos
        self.ana = User.objects.create_user(username="ana", password="clave12345")
        self.luis = User.objects.create_user(username="luis", password="clave12345")

        # Cada uno con sus propios posts
        Post.objects.create(author=self.ana, content="Post de ana 1")
        Post.objects.create(author=self.ana, content="Post de ana 2")
        Post.objects.create(author=self.luis, content="Post de luis 1")

        # Autenticamos el cliente de test como "ana".
        # force_authenticate() es un atajo de DRF para pruebas: simula que
        # "ana" ya inició sesión, sin necesidad de generar un token JWT real.
        self.client.force_authenticate(user=self.ana)

    def test_my_posts_solo_devuelve_los_propios(self):
        url = reverse('posts_api:my_posts')
        response = self.client.get(url)

        # La petición debe ser exitosa
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Extraemos el autor de cada post que vino en la respuesta
        usernames_en_respuesta = [
            post["author_username"] for post in response.data
        ]

        # TODOS los posts devueltos deben ser de "ana" (nadie más)
        self.assertEqual(set(usernames_en_respuesta), {"ana"})

        # Y deben ser exactamente los 2 posts que le pertenecen a ana
        # (ni de más, ni de menos)
        self.assertEqual(len(response.data), 2)


class PostInexistenteTests(APITestCase):
    """
    Test de integración: pedir comentarios (o comentar) sobre un post
    que NO existe debe responder 404 Not Found, no 400 Bad Request.

    ¿Por qué este test es útil?
    Antes, CreateCommentAPIView y PostCommentAPIView respondían 400
    cuando el post no existía. Semánticamente eso está mal: 400
    significa "tu petición está mal formada" (por ejemplo, un campo
    faltante); 404 significa "el recurso que pides no existe". Además,
    el módulo de chat (ConversationsMessagesAPIView) ya usaba 404
    correctamente para este mismo caso, así que era una inconsistencia
    entre módulos del mismo proyecto.
    """

    def setUp(self):
        self.ana = User.objects.create_user(username="ana", password="clave12345")
        self.client.force_authenticate(user=self.ana)

    def test_comentar_post_inexistente_da_404(self):
        # 9999 es un id que no existe en la base de datos de prueba
        url = reverse('posts_api:create_comment', args=[9999])
        response = self.client.post(url, {"content": "hola"})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_ver_comentarios_de_post_inexistente_da_404(self):
        url = reverse('posts_api:post_comments', args=[9999])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
