from django.shortcuts import render

# Create your views here.
def feed_page(request):
    return render(request,"posts/feed.html")

# COMENTARIO DE PRUEBA
# COEMNTARIO FINAL