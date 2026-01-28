from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    @property
    def is_profesor(self):
        return hasattr(self, 'profesor')

    @property
    def is_estudiante(self):
        return hasattr(self, 'estudiante')

class Carrera(models.Model):
    nombre = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre
class Estudiante(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    año = models.IntegerField()
    carrera = models.ForeignKey('login.Carrera', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.año} - {self.carrera}"
    
class Profesor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    carrera = models.ForeignKey('login.Carrera', on_delete=models.CASCADE, null=True, blank=True)
    nivel = models.CharField(max_length=20, choices=[('profesor', 'Profesor'), ('jefe de carrera', 'Jefe de Carrera')], default='profesor')
    materias = models.ManyToManyField('login.Materia', related_name='profesores', blank=True)
    foto = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.carrera.nombre if self.carrera else 'Sin carrera'}"
    
class Materia (models.Model):
    nombre = models.CharField(max_length=100)
    carrera = models.ForeignKey('login.Carrera', on_delete=models.CASCADE)

    año = models.IntegerField(default=1)
    progreso_temario = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nombre}"
    
class Nota(models.Model):
    estudiante = models.ForeignKey('login.Estudiante', on_delete=models.CASCADE, related_name='notas')
    materia = models.ForeignKey('login.Materia', on_delete=models.CASCADE)
    valor = models.FloatField()
    tendencia = models.CharField(max_length=10, choices=[('subio', 'Subió'), ('bajo', 'Bajó'), ('mantuvo', 'Mantuvo')], default='mantuvo')

    def __str__(self):
        return f"{self.estudiante.user.username} - {self.materia.nombre} - {self.valor}"

class Horario(models.Model):
    materia = models.ForeignKey('login.Materia', on_delete=models.CASCADE)
    dia = models.CharField(max_length=15)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    aula = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        aula_str = f" - {self.aula}" if self.aula else ""
        return f"{self.materia.nombre} - {self.dia} {self.hora_inicio}-{self.hora_fin}{aula_str}"  

class Noticia(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    categoria = models.CharField(max_length=20, choices=[('examen', 'Examen'), ('evento', 'Evento'), ('aviso', 'Aviso')], default='aviso')
    visible_para = models.CharField(max_length=20, choices=[('estudiantes', 'Estudiantes'), ('profesores', 'Profesores'), ('todos', 'Todos')])
    carrera =  models.ForeignKey('login.Carrera', on_delete=models.CASCADE, null=True, blank=True)
    anio = models.IntegerField(null=True, blank=True)
    autor = models.ForeignKey('login.Profesor', on_delete=models.CASCADE, null=True, blank=True, related_name='noticias_publicadas')

    def __str__(self):
        return self.titulo