# 🎓 Sistema Académico UHO

Sistema de gestión académica desarrollado con Django para la Universidad de Holguín. Permite la administración de estudiantes, profesores, materias, horarios y calificaciones.

## ✨ Características Principales

### Para Estudiantes
- 📚 **Dashboard personalizado** con próxima clase y horario completo
- 📊 **Visualización de notas** con indicadores de tendencia (subió/bajó/mantuvo)
- 📰 **Feed de noticias** segmentado por carrera y año
- 🕐 **Horario semanal** con información de aulas y horarios

### Para Profesores
- 👨‍🏫 **Gestión de asignaturas** asignadas
- 📝 **Subida masiva de notas** mediante archivos Excel
- 📢 **Publicación de noticias** con segmentación por audiencia
- 👥 **Visualización de estudiantes** con sus calificaciones por materia

### Para Jefes de Carrera
- 🔧 **Asignación de profesores** a materias
- 📅 **Carga masiva de horarios** mediante Excel
- 👥 **Gestión completa de profesores** de la carrera

## 🛠️ Tecnologías Utilizadas

- **Backend:** Django 5.2.8
- **Base de Datos:** SQLite
- **Frontend:** Bootstrap 5, JavaScript Vanilla
- **Procesamiento:** openpyxl (archivos Excel)
- **Autenticación:** Django Auth con perfiles extendidos

## 📋 Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd se
```

### 2. Crear entorno virtual
```bash
python -m venv venv
```

### 3. Activar entorno virtual
**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Aplicar migraciones
```bash
python manage.py migrate
```

### 6. Crear superusuario (opcional)
```bash
python manage.py createsuperuser
```

### 7. Ejecutar servidor
```bash
python manage.py runserver
```

El sistema estará disponible en: `http://localhost:8000`

## 👤 Tipos de Usuario

El sistema determina el rol del usuario según el dominio del email:

- `@estudiante.com` → **Estudiante**
- `@profesor.com` → **Profesor**
- `@jefedecarrera.com` → **Jefe de Carrera**

### Registro
1. Ir a la página principal
2. Hacer clic en "Crear Cuenta"
3. Completar el formulario con:
   - Nombre de usuario
   - Email (con dominio correspondiente al rol deseado)
   - Contraseña
   - Carrera
   - Año (solo para estudiantes)

## 📁 Estructura del Proyecto

```
se/
├── manage.py                 # Comando principal de Django
├── db.sqlite3               # Base de datos
├── requirements.txt         # Dependencias Python
│
├── login/                   # App principal
│   ├── models.py           # Modelos (User, Estudiante, Profesor, etc.)
│   ├── views.py            # Vistas y APIs
│   ├── urls.py             # Rutas
│   └── admin.py            # Configuración del admin
│
├── se/                      # Configuración Django
│   ├── settings.py         # Configuración general
│   └── urls.py             # URLs principales
│
├── templates/               # Templates HTML
│   ├── base.html           # Template base
│   ├── login.html          # Login y registro
│   ├── profesor.html       # Dashboard profesor
│   └── estudiante.html     # Dashboard estudiante
│
└── static/                  # Archivos estáticos
    ├── css/                # Hojas de estilo
    └── js/                 # JavaScript
```

## 📊 Modelos de Base de Datos

- **User:** Usuario base con autenticación
- **Carrera:** Carreras universitarias
- **Estudiante:** Perfil de estudiante (año, carrera)
- **Profesor:** Perfil de profesor (nivel, materias)
- **Materia:** Asignaturas del plan de estudios
- **Nota:** Calificaciones de estudiantes
- **Horario:** Programación de clases
- **Noticia:** Sistema de anuncios

## 📝 Funcionalidades Detalladas

### Subir Notas (Profesores)
1. Ir a "Subir Notas"
2. Seleccionar carrera, año y materia
3. Subir archivo Excel con formato:
   ```
   | Nombre (username) | Nota |
   |-------------------|------|
   | juan_perez        | 4.5  |
   ```
4. El sistema calcula automáticamente las tendencias

### Subir Horarios (Jefes de Carrera)
1. Ir a "Subir Horarios"
2. Seleccionar carrera y año
3. Subir archivo Excel con formato:
   ```
   | Materia      | Día   | Hora Inicio | Hora Fin | Aula |
   |--------------|-------|-------------|----------|------|
   | Matemática I | Lunes | 08:00       | 10:00    | A101 |
   ```

### Gestión de Profesores (Jefes de Carrera)
1. Ir a "Gestión de Profesores"
2. Seleccionar profesor de la lista
3. Asignar carrera y materias
4. Guardar cambios

## 🔒 Seguridad

- Autenticación requerida para todas las vistas principales
- Validación de permisos por rol
- CSRF protection en formularios
- Sesiones configurables (recordar sesión)

## 📖 Documentación Adicional

- `INSTRUCCIONES_SUBIR_NOTAS.md` - Guía detallada para subir notas
- `INSTRUCCIONES_SUBIR_HORARIOS.md` - Guía detallada para subir horarios

## 🐛 Solución de Problemas

### El servidor no inicia
```bash
# Verificar que el entorno virtual esté activado
# Reinstalar dependencias
pip install -r requirements.txt
```

### Error de base de datos
```bash
# Eliminar db.sqlite3 y volver a migrar
python manage.py migrate
```

### Archivos estáticos no cargan
```bash
# Recolectar archivos estáticos
python manage.py collectstatic
```

## 👥 Contribuidores

Proyecto desarrollado para la Universidad de Holguín

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-☕-yellow?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/hche)

> *"Un café = Un bug menos en tu código"* - Proverbio de programador 🐛☕


## 📄 Licencia

Este proyecto es de uso académico.

---

**Última actualización:** Enero 2026  
**Cafés consumidos durante el desarrollo:** ∞
