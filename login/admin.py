from django.contrib import admin
from .models import User, Carrera, Estudiante, Profesor, Materia, Nota, Horario, Noticia

class EstudianteInline(admin.StackedInline):
    model = Estudiante
    extra = 1

class ProfesorInline(admin.StackedInline):
    model = Profesor
    extra = 1

# Registro del modelo User
admin.site.register(User)

# Registro del modelo Carrera
class CarreraAdmin(admin.ModelAdmin):
    inlines = [EstudianteInline]  # Muestra a los estudiantes relacionados
admin.site.register(Carrera, CarreraAdmin)

# Registro del modelo Estudiante
admin.site.register(Estudiante)

# Registro del modelo Profesor
admin.site.register(Profesor)

# Registro del modelo Materia
admin.site.register(Materia)

# Registro del modelo Nota
admin.site.register(Nota)

# Registro del modelo Horario
admin.site.register(Horario)

# Registro del modelo Noticia
admin.site.register(Noticia)

