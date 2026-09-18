from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Profile


class RegistroCreaPerfilTests(APITestCase):
    """
    Test de integración: al registrar un usuario nuevo a través de la API,
    Django debe crear automáticamente su Profile asociado (OneToOneField).

    ¿Por qué este test es útil?
    RegisterAPIView (accounts/api_views.py) hace DOS pasos seguidos:
        1) User.objects.create_user(...)
        2) Profile.objects.create(user=user)

    Si alguien borra o rompe el paso 2 por accidente (por ejemplo, al
    refactorizar la vista), el usuario queda registrado pero SIN perfil.
    Más adelante, cualquier vista que use `request.user.profile`
    (como MeAPIView o UpdateProfileView) explotaría con un error.

    Este test existe para atrapar justo ese tipo de error antes de
    que llegue a producción.
    """

    def test_registro_crea_profile_asociado(self):
        # APITestCase nos da self.client, un cliente HTTP de prueba
        # que no necesita un servidor real corriendo.
        url = reverse('accounts_api:register')

        datos_de_registro = {
            "username": "franco",
            "email": "franco@test.com",
            "password": "clave12345",
            "password2": "clave12345",
        }

        response = self.client.post(url, datos_de_registro)

        # 1) La petición debe responder 201 Created (registro exitoso)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 2) El User debe existir realmente en la base de datos de prueba
        usuario_creado = User.objects.get(username="franco")

        # 3) Debe existir un Profile en la base de datos ligado a ESE usuario
        self.assertTrue(
            Profile.objects.filter(user=usuario_creado).exists()
        )

        # 4) Acceder a usuario.profile (la relación inversa del OneToOneField)
        #    no debe lanzar un error de "Profile no existe"
        self.assertIsNotNone(usuario_creado.profile)


class EmailDuplicadoTests(APITestCase):
    """
    Test de integración: el registro debe rechazar un email que ya
    existe, SIN IMPORTAR las mayúsculas/minúsculas con las que se
    escriba.

    ¿Por qué este test es útil?
    Antes, RegisterAPIView comparaba el email así:
        User.objects.filter(email=email).exists()
    Esa comparación es sensible a mayúsculas: "Test@Test.com" y
    "test@test.com" se trataban como emails DISTINTOS, permitiendo
    crear dos cuentas con el mismo correo (solo cambiando el casing).

    Ahora se usa `email__iexact=email`, que compara ignorando
    mayúsculas/minúsculas, tal como se espera de un email.
    """

    def test_email_duplicado_no_distingue_mayusculas(self):
        # Usuario ya registrado con email en minúsculas
        User.objects.create_user(
            username="user1", email="test@test.com", password="ClaveSegura#2024"
        )

        url = reverse('accounts_api:register')
        datos_de_registro = {
            "username": "user2",
            "email": "Test@Test.com",  # mismo email, distinto casing
            "password": "OtraClaveSegura#2024",
            "password2": "OtraClaveSegura#2024",
        }

        response = self.client.post(url, datos_de_registro)

        # Debe rechazarse por email duplicado
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Y "user2" NO debe haberse creado
        self.assertEqual(User.objects.filter(username="user2").count(), 0)


class PasswordDebilTests(APITestCase):
    """
    Test de integración: una contraseña débil (por ejemplo, solo
    números) debe ser rechazada en el registro.

    ¿Por qué este test es útil?
    Antes, RegisterAPIView solo validaba la LONGITUD de la contraseña:
        if len(password) < 8:
    Una contraseña como "12345678" tiene 8 caracteres, así que pasaba
    sin problema, aunque sea trivial de adivinar.

    El proyecto ya tenía configurados en settings.py los validadores
    estándar de Django (AUTH_PASSWORD_VALIDATORS), incluyendo
    NumericPasswordValidator (rechaza contraseñas solo numéricas),
    pero RegisterAPIView nunca los llamaba. Ahora se usa
    validate_password(), que sí los activa.
    """

    def test_password_totalmente_numerica_es_rechazada(self):
        url = reverse('accounts_api:register')
        datos_de_registro = {
            "username": "franco",
            "email": "franco@test.com",
            "password": "12345678",
            "password2": "12345678",
        }

        response = self.client.post(url, datos_de_registro)

        # Debe rechazarse por ser una contraseña débil
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Y el usuario NO debe haberse creado
        self.assertEqual(User.objects.filter(username="franco").count(), 0)

    def test_password_segura_es_aceptada(self):
        # Caso de control: una contraseña razonable SÍ debe funcionar,
        # para confirmar que no nos pasamos de estrictos.
        url = reverse('accounts_api:register')
        datos_de_registro = {
            "username": "franco",
            "email": "franco@test.com",
            "password": "ClaveSegura#2024",
            "password2": "ClaveSegura#2024",
        }

        response = self.client.post(url, datos_de_registro)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# TEST BASURA — solo para probar el gate "Wait for CI" de Railway. BORRAR después de probar.
from rest_framework.test import APITestCase as _APITestCase


class ZZZTestDummyFallaSiempreTests(_APITestCase):
    def test_esto_falla_a_proposito(self):
        self.assertEqual(1, 2, "Falla a propósito para probar el CI gate")
