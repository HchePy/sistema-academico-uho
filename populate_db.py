<<<<<<< HEAD
"""
Script para poblar la base de datos con carreras y materias iniciales
Ejecutar con: python manage.py shell < populate_db.py
O: python manage.py runscript populate_db (si tienes django-extensions)
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'se.settings')
django.setup()

from login.models import Carrera, Materia

def populate_database():
    print("🚀 Iniciando población de la base de datos...")
    
    # Definir carreras y sus materias por año
    carreras_data = {
        "Ingeniería Informática": {
            1: ["Matemática I", "Programación I", "Introducción a la Informática", "Física I", "Inglés I"],
            2: ["Matemática II", "Programación II", "Estructuras de Datos", "Física II", "Inglés II"],
            3: ["Bases de Datos", "Sistemas Operativos", "Redes de Computadoras", "Ingeniería de Software I", "Matemática Numérica"],
            4: ["Inteligencia Artificial", "Compiladores", "Ingeniería de Software II", "Seguridad Informática", "Gestión de Proyectos"],
            5: ["Trabajo de Diploma", "Sistemas Distribuidos", "Computación Gráfica", "Optativa I", "Optativa II"]
        },
        "Ingeniería Eléctrica": {
            1: ["Matemática I", "Física I", "Química", "Dibujo Técnico", "Introducción a la Ingeniería"],
            2: ["Matemática II", "Física II", "Circuitos Eléctricos I", "Electrónica I", "Mecánica"],
            3: ["Circuitos Eléctricos II", "Electrónica II", "Máquinas Eléctricas I", "Teoría de Control", "Mediciones Eléctricas"],
            4: ["Máquinas Eléctricas II", "Sistemas de Potencia", "Electrónica de Potencia", "Automatización", "Instalaciones Eléctricas"],
            5: ["Trabajo de Diploma", "Energías Renovables", "Protecciones Eléctricas", "Optativa I", "Optativa II"]
        },
        "Ingeniería Mecánica": {
            1: ["Matemática I", "Física I", "Química", "Dibujo Técnico", "Introducción a la Ingeniería"],
            2: ["Matemática II", "Física II", "Resistencia de Materiales", "Termodinámica", "Mecánica de Fluidos"],
            3: ["Diseño Mecánico I", "Tecnología de los Materiales", "Máquinas Térmicas", "Mecanismos", "CAD/CAM"],
            4: ["Diseño Mecánico II", "Manufactura", "Mantenimiento Industrial", "Vibraciones Mecánicas", "Hidráulica y Neumática"],
            5: ["Trabajo de Diploma", "Gestión de la Producción", "Refrigeración", "Optativa I", "Optativa II"]
        },
        "Licenciatura en Contabilidad": {
            1: ["Matemática Financiera", "Introducción a la Contabilidad", "Economía I", "Derecho I", "Informática"],
            2: ["Contabilidad Financiera I", "Economía II", "Estadística", "Derecho II", "Administración I"],
            3: ["Contabilidad Financiera II", "Contabilidad de Costos", "Finanzas I", "Auditoría I", "Administración II"],
            4: ["Contabilidad Gerencial", "Finanzas II", "Auditoría II", "Tributación", "Análisis Financiero"],
            5: ["Trabajo de Diploma", "Contabilidad Internacional", "Ética Profesional", "Optativa I", "Optativa II"]
        },
        "Licenciatura en Economía": {
            1: ["Matemática I", "Introducción a la Economía", "Contabilidad", "Historia Económica", "Informática"],
            2: ["Matemática II", "Microeconomía", "Macroeconomía", "Estadística I", "Derecho Económico"],
            3: ["Econometría", "Economía Internacional", "Finanzas", "Estadística II", "Política Económica"],
            4: ["Economía del Desarrollo", "Economía Empresarial", "Mercados Financieros", "Planificación Económica", "Investigación de Operaciones"],
            5: ["Trabajo de Diploma", "Economía Ambiental", "Evaluación de Proyectos", "Optativa I", "Optativa II"]
        },
        "Licenciatura en Derecho": {
            1: ["Introducción al Derecho", "Derecho Romano", "Teoría del Estado", "Historia del Derecho", "Metodología de la Investigación"],
            2: ["Derecho Civil I", "Derecho Penal I", "Derecho Constitucional", "Derecho Administrativo I", "Filosofía del Derecho"],
            3: ["Derecho Civil II", "Derecho Penal II", "Derecho Procesal Civil", "Derecho Administrativo II", "Derecho Laboral"],
            4: ["Derecho Mercantil", "Derecho Procesal Penal", "Derecho Internacional Público", "Derecho Financiero", "Derecho Ambiental"],
            5: ["Trabajo de Diploma", "Derecho Internacional Privado", "Práctica Jurídica", "Optativa I", "Optativa II"]
        }
    }
    
    # Contador de registros creados
    carreras_creadas = 0
    materias_creadas = 0
    
    # Crear carreras y materias
    for carrera_nombre, materias_por_anio in carreras_data.items():
        # Crear o obtener la carrera
        carrera, created = Carrera.objects.get_or_create(nombre=carrera_nombre)
        if created:
            carreras_creadas += 1
            print(f"✅ Carrera creada: {carrera_nombre}")
        else:
            print(f"ℹ️  Carrera ya existe: {carrera_nombre}")
        
        # Crear materias para cada año
        for anio, materias_lista in materias_por_anio.items():
            for materia_nombre in materias_lista:
                materia, created = Materia.objects.get_or_create(
                    nombre=materia_nombre,
                    carrera=carrera,
                    año=anio,
                    defaults={'progreso_temario': 0}
                )
                if created:
                    materias_creadas += 1
                    print(f"  📚 Materia creada: {materia_nombre} (Año {anio})")
    
    print("\n" + "="*60)
    print(f"✨ Población completada exitosamente!")
    print(f"📊 Resumen:")
    print(f"   - Carreras creadas: {carreras_creadas}")
    print(f"   - Materias creadas: {materias_creadas}")
    print(f"   - Total de carreras en BD: {Carrera.objects.count()}")
    print(f"   - Total de materias en BD: {Materia.objects.count()}")
    print("="*60)

if __name__ == "__main__":
    populate_database()
=======
"""
Script para poblar la base de datos con carreras y materias iniciales
Ejecutar con: python manage.py shell < populate_db.py
O: python manage.py runscript populate_db (si tienes django-extensions)
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'se.settings')
django.setup()

from login.models import Carrera, Materia

def populate_database():
    print("🚀 Iniciando población de la base de datos...")
    
    # Definir carreras y sus materias por año
    carreras_data = {
        "Ingeniería Informática": {
            1: ["Matemática I", "Programación I", "Introducción a la Informática", "Física I", "Inglés I"],
            2: ["Matemática II", "Programación II", "Estructuras de Datos", "Física II", "Inglés II"],
            3: ["Bases de Datos", "Sistemas Operativos", "Redes de Computadoras", "Ingeniería de Software I", "Matemática Numérica"],
            4: ["Inteligencia Artificial", "Compiladores", "Ingeniería de Software II", "Seguridad Informática", "Gestión de Proyectos"],
            5: ["Trabajo de Diploma", "Sistemas Distribuidos", "Computación Gráfica", "Optativa I", "Optativa II"]
        },
        "Ingeniería Eléctrica": {
            1: ["Matemática I", "Física I", "Química", "Dibujo Técnico", "Introducción a la Ingeniería"],
            2: ["Matemática II", "Física II", "Circuitos Eléctricos I", "Electrónica I", "Mecánica"],
            3: ["Circuitos Eléctricos II", "Electrónica II", "Máquinas Eléctricas I", "Teoría de Control", "Mediciones Eléctricas"],
            4: ["Máquinas Eléctricas II", "Sistemas de Potencia", "Electrónica de Potencia", "Automatización", "Instalaciones Eléctricas"],
            5: ["Trabajo de Diploma", "Energías Renovables", "Protecciones Eléctricas", "Optativa I", "Optativa II"]
        },
        "Ingeniería Mecánica": {
            1: ["Matemática I", "Física I", "Química", "Dibujo Técnico", "Introducción a la Ingeniería"],
            2: ["Matemática II", "Física II", "Resistencia de Materiales", "Termodinámica", "Mecánica de Fluidos"],
            3: ["Diseño Mecánico I", "Tecnología de los Materiales", "Máquinas Térmicas", "Mecanismos", "CAD/CAM"],
            4: ["Diseño Mecánico II", "Manufactura", "Mantenimiento Industrial", "Vibraciones Mecánicas", "Hidráulica y Neumática"],
            5: ["Trabajo de Diploma", "Gestión de la Producción", "Refrigeración", "Optativa I", "Optativa II"]
        },
        "Licenciatura en Contabilidad": {
            1: ["Matemática Financiera", "Introducción a la Contabilidad", "Economía I", "Derecho I", "Informática"],
            2: ["Contabilidad Financiera I", "Economía II", "Estadística", "Derecho II", "Administración I"],
            3: ["Contabilidad Financiera II", "Contabilidad de Costos", "Finanzas I", "Auditoría I", "Administración II"],
            4: ["Contabilidad Gerencial", "Finanzas II", "Auditoría II", "Tributación", "Análisis Financiero"],
            5: ["Trabajo de Diploma", "Contabilidad Internacional", "Ética Profesional", "Optativa I", "Optativa II"]
        },
        "Licenciatura en Economía": {
            1: ["Matemática I", "Introducción a la Economía", "Contabilidad", "Historia Económica", "Informática"],
            2: ["Matemática II", "Microeconomía", "Macroeconomía", "Estadística I", "Derecho Económico"],
            3: ["Econometría", "Economía Internacional", "Finanzas", "Estadística II", "Política Económica"],
            4: ["Economía del Desarrollo", "Economía Empresarial", "Mercados Financieros", "Planificación Económica", "Investigación de Operaciones"],
            5: ["Trabajo de Diploma", "Economía Ambiental", "Evaluación de Proyectos", "Optativa I", "Optativa II"]
        },
        "Licenciatura en Derecho": {
            1: ["Introducción al Derecho", "Derecho Romano", "Teoría del Estado", "Historia del Derecho", "Metodología de la Investigación"],
            2: ["Derecho Civil I", "Derecho Penal I", "Derecho Constitucional", "Derecho Administrativo I", "Filosofía del Derecho"],
            3: ["Derecho Civil II", "Derecho Penal II", "Derecho Procesal Civil", "Derecho Administrativo II", "Derecho Laboral"],
            4: ["Derecho Mercantil", "Derecho Procesal Penal", "Derecho Internacional Público", "Derecho Financiero", "Derecho Ambiental"],
            5: ["Trabajo de Diploma", "Derecho Internacional Privado", "Práctica Jurídica", "Optativa I", "Optativa II"]
        }
    }
    
    # Contador de registros creados
    carreras_creadas = 0
    materias_creadas = 0
    
    # Crear carreras y materias
    for carrera_nombre, materias_por_anio in carreras_data.items():
        # Crear o obtener la carrera
        carrera, created = Carrera.objects.get_or_create(nombre=carrera_nombre)
        if created:
            carreras_creadas += 1
            print(f"✅ Carrera creada: {carrera_nombre}")
        else:
            print(f"ℹ️  Carrera ya existe: {carrera_nombre}")
        
        # Crear materias para cada año
        for anio, materias_lista in materias_por_anio.items():
            for materia_nombre in materias_lista:
                materia, created = Materia.objects.get_or_create(
                    nombre=materia_nombre,
                    carrera=carrera,
                    año=anio,
                    defaults={'progreso_temario': 0}
                )
                if created:
                    materias_creadas += 1
                    print(f"  📚 Materia creada: {materia_nombre} (Año {anio})")
    
    print("\n" + "="*60)
    print(f"✨ Población completada exitosamente!")
    print(f"📊 Resumen:")
    print(f"   - Carreras creadas: {carreras_creadas}")
    print(f"   - Materias creadas: {materias_creadas}")
    print(f"   - Total de carreras en BD: {Carrera.objects.count()}")
    print(f"   - Total de materias en BD: {Materia.objects.count()}")
    print("="*60)

if __name__ == "__main__":
    populate_database()
>>>>>>> 7e5fb0d16e8bb2bbc9b7521f0fd17a7bec9c5001
