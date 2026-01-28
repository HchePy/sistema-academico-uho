from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro_view, name='registro'),
    path('noticias/crear/', views.crear_noticia, name='crear_noticia'),
    path('noticias/borrar/<int:noticia_id>/', views.borrar_noticia, name='borrar_noticia'),
    path('noticias/editar/<int:noticia_id>/', views.editar_noticia, name='editar_noticia'),
    path('api/materias/', views.get_materias_api, name='api-materias'),
    path('subir-notas/', views.subir_notas, name='subir_notas'),
    path('subir-horarios/', views.subir_horarios, name='subir_horarios'),
    path('api/profesores/asignar/', views.asignar_profesor_api, name='api-asignar-profesor'),
    path('api/obtener-estudiantes-notas/<int:materia_id>/', views.obtener_estudiantes_notas_api, name='api-obtener-estudiantes-notas'),
]
