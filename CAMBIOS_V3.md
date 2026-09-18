# Cambios en v3 respecto a v2 — Testing

Este documento explica qué se agregó y qué se modificó en `miRedSocial_v3`
respecto a `miRedSocial_v2`, como parte del ejercicio de testing de la clase.
El objetivo fue: (1) escribir tests automatizados con `APITestCase` de DRF,
y (2) corregir el código donde los tests revelaron comportamiento incorrecto.

No se tocó nada del script de despliegue (`.github/workflows/deploy.yml`).

---

## 1. Tests agregados (antes no existía ningún test real)

En `v2`, los tres archivos `tests.py` estaban vacíos (solo el boilerplate
que genera Django por defecto). En `v3` se agregaron **9 tests** repartidos
en las tres apps.

### `accounts/tests.py`

| Clase | Qué verifica | ¿Pasaba en v2 sin cambios? |
|---|---|---|
| `RegistroCreaPerfilTests` | Al registrar un usuario, se crea automáticamente su `Profile` asociado | ✅ Sí, ya funcionaba |
| `EmailDuplicadoTests` | No se puede registrar dos veces el mismo email con distinto casing (`Test@Test.com` vs `test@test.com`) | ❌ No — requirió cambio de código |
| `PasswordDebilTests` | Una contraseña débil (ej. `"12345678"`) es rechazada; una contraseña razonable sí se acepta | ❌ No — requirió cambio de código |

### `posts/tests.py`

| Clase | Qué verifica | ¿Pasaba en v2 sin cambios? |
|---|---|---|
| `MisPostsAislamientoTests` | El endpoint `/api/posts/my/` solo devuelve posts del usuario autenticado, no de otros | ✅ Sí, ya funcionaba |
| `PostInexistenteTests` | Comentar o ver comentarios de un post que no existe responde **404**, no 400 | ❌ No — requirió cambio de código |

### `chat/tests.py`

| Clase | Qué verifica | ¿Pasaba en v2 sin cambios? |
|---|---|---|
| `ConversacionSinDuplicadosTests` | Iniciar conversación en cualquier sentido (A→B o B→A) siempre da la misma conversación, nunca duplica | ✅ Sí, ya funcionaba |
| `NoAutoChatTests` | Un usuario no puede iniciar una conversación consigo mismo | ✅ Sí, ya funcionaba |
| `AislamientoConversacionesAjenasTests` | Un usuario que no participa en una conversación no puede leer ni enviar mensajes en ella (403) | ✅ Sí, ya funcionaba |
| `MensajeVacioRechazadoTests` | El serializer `CreateMessageSerializer` rechaza contenido vacío o solo espacios | ✅ Sí, ya funcionaba |

**Resumen:** 6 de los 9 tests documentan comportamiento que ya era correcto
(sirven como red de seguridad a futuro). 3 tests encontraron comportamiento
real a corregir, detallado abajo.

---

## 2. Cambios de código para que los tests pasen

### a) `accounts/api_views.py` — Email duplicado insensible a mayúsculas

**Antes:**
```python
if User.objects.filter(email=email).exists():
```

**Ahora:**
```python
if User.objects.filter(email__iexact=email).exists():
```

`filter(email=...)` compara el email de forma exacta (sensible a
mayúsculas). Con `__iexact`, Django compara ignorando mayúsculas/
minúsculas, que es el comportamiento correcto para un email.

---

### b) `accounts/api_views.py` — Validación real de contraseña

**Antes:**
```python
if len(password) < 8:
    return Response(
        {"error": "La contraseña debe contener mas de 8 caracteres"},
        status=status.HTTP_400_BAD_REQUEST
    )
```

**Ahora:**
```python
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

# ...

try:
    validate_password(password)
except DjangoValidationError as e:
    return Response(
        {"error": list(e.messages)},
        status=status.HTTP_400_BAD_REQUEST
    )
```

El proyecto ya tenía configurados en `settings.py` los validadores
estándar de Django (`AUTH_PASSWORD_VALIDATORS`), pero `RegisterAPIView`
nunca los llamaba — solo revisaba la longitud. Ahora se usa
`validate_password()`, que activa automáticamente:
- `MinimumLengthValidator` (longitud mínima)
- `CommonPasswordValidator` (rechaza contraseñas muy comunes, ej. `"password"`)
- `NumericPasswordValidator` (rechaza contraseñas solo numéricas, ej. `"12345678"`)
- `UserAttributeSimilarityValidator` (rechaza contraseñas muy parecidas al username/email)

---

### c) `posts/api_views.py` — Código de estado correcto para "no existe"

**Antes** (en `CreateCommentAPIView` y `PostCommentAPIView`):
```python
except Post.DoesNotExist:
    return Response(
        {'error': "Post no encontrado"},
        status=status.HTTP_400_BAD_REQUEST
    )
```

**Ahora:**
```python
except Post.DoesNotExist:
    return Response(
        {'error': "Post no encontrado"},
        status=status.HTTP_404_NOT_FOUND
    )
```

`400 Bad Request` significa "tu petición está mal formada" (por ejemplo,
falta un campo obligatorio). `404 Not Found` significa "el recurso que
pides no existe". Comentar sobre un post inexistente es el segundo caso,
no el primero. Este mismo patrón ya se usaba correctamente en
`chat/api_views.py` (`ConversationsMessagesAPIView`), así que este cambio
también deja consistente el criterio entre módulos del proyecto.

---

## 3. Cómo correr los tests

```bash
cd miRedSocial_v3
python manage.py test accounts posts chat
```

O por app individual, por ejemplo solo accounts:
```bash
python manage.py test accounts
```

Con verbosidad para ver el nombre de cada test al correr:
```bash
python manage.py test accounts posts chat --verbosity 2
```

---

## 4. Pendiente (fuera del alcance de esta sesión)

El test de `is_private` (perfil privado) **no** se implementó todavía:
el campo existe en el modelo `Profile` y se puede editar desde
`UpdateProfileView`, pero ningún endpoint lo respeta actualmente
(`UserListAPIView` devuelve el perfil completo de todos los usuarios sin
filtrar). A diferencia de los otros 3, este requiere primero decidir la
regla de negocio (qué datos exactamente se ocultan y a quién) antes de
poder escribir el test y el fix.
