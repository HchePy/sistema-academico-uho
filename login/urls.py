from django.urls import path
from . import views

urlpatterns = [
    path('api/register/', views.register_api, name='api-register'),
    path('api/login/', views.login_api, name='api-login'),
    path('api/noticias/crear/', views.crear_noticia_api, name='api-crear-noticia'),
    path('api/noticias/mias/', views.get_mis_noticias_api, name='api-mis-noticias'),
    path('api/noticias/borrar/<int:noticia_id>/', views.borrar_noticia_api, name='api-borrar-noticia'),
    path('api/noticias/editar/<int:noticia_id>/', views.editar_noticia_api, name='api-editar-noticia'),
    path('api/materias/', views.get_materias_api, name='api-materias'),
    path('subir-notas/', views.subir_notas, name='subir_notas'),
    path('subir-horarios/', views.subir_horarios, name='subir_horarios'),
    path('api/profesores/asignar/', views.asignar_profesor_api, name='api-asignar-profesor'),
    path('api/obtener-estudiantes-notas/<int:materia_id>/', views.obtener_estudiantes_notas_api, name='api-obtener-estudiantes-notas'),
]
