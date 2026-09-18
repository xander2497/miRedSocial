# --- Imagen base ---
# Python 3.12 en su variante "slim": liviana pero con lo justo para correr Python.
FROM python:3.12-slim

# --- Variables de entorno de Python ---
# PYTHONDONTWRITEBYTECODE: no genera archivos .pyc (no aportan nada dentro del contenedor)
# PYTHONUNBUFFERED: los logs de Django/gunicorn salen al instante en Railway, sin buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Carpeta de trabajo dentro del contenedor. Todo lo que sigue se ejecuta desde aquí.
WORKDIR /app

# --- Dependencias del sistema operativo ---
# Pillow (usado para las imágenes de avatar/posts) necesita estas librerías
# de compilación de imagenes del sistema para poder instalarse correctamente.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# --- Dependencias de Python ---
# Se copia SOLO requirements.txt primero (antes que el resto del código).
# Así, si no cambias las dependencias, Docker reutiliza esta capa cacheada
# y no reinstala todo cada vez que editas un archivo .py.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Código de la app ---
# Ahora sí se copia todo el proyecto (accounts/, posts/, chat/, templates/, etc.)
COPY . .

# --- Archivos estáticos ---
# Junta el CSS/JS del admin de Django y de DRF en una sola carpeta (STATIC_ROOT)
# para que un servidor los pueda entregar en producción.
RUN python manage.py collectstatic --noinput

# Puerto por defecto para pruebas locales (docker run -p 8000:8000).
# Railway ignora este valor: inyecta su propio $PORT en tiempo de ejecución.
EXPOSE 8000

# --- Comando de arranque ---
# gunicorn es el servidor de producción (Django's runserver NO se usa en prod).
# miRedSocial.wsgi:application apunta a miRedSocial/wsgi.py -> variable "application".
# ${PORT:-8000}: usa la variable PORT que inyecta Railway; si no existe (ej. local), usa 8000.
# Debe ir en forma "shell" (sin corchetes) para que ${...} se expanda.
CMD gunicorn miRedSocial.wsgi:application --bind 0.0.0.0:${PORT:-8000}
