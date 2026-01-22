from django.shortcuts import render, redirect
from django.db import models

from .models import User, Estudiante, Profesor, Carrera, Materia, Nota, Horario, Noticia
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Q

import json
import os
from django.http import JsonResponse
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt

import openpyxl

def logout_view(request):
    logout(request)
    return redirect('login')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('base')
    carreras = Carrera.objects.all()
    # Noticias públicas para el carrusel (visible para todos)
    noticias_globales = Noticia.objects.filter(visible_para='todos').order_by('-fecha_publicacion')[:3]
    return render(request, 'login.html', {
        'carreras': carreras,
        'noticias_globales': noticias_globales
    })

@login_required
def base_view(request):
    if request.user.is_profesor:
        try:
            profesor = request.user.profesor
            materias = profesor.materias.all()
            
            # Métricas para el profesor
            total_alumnos = Estudiante.objects.filter(carrera=profesor.carrera).count()
            # Noticias para el profesor
            noticias_profesor = Noticia.objects.filter(
                Q(visible_para='todos') |
                (Q(visible_para='profesores') & (Q(carrera=profesor.carrera) | Q(carrera__isnull=True)))
            ).order_by('-fecha_publicacion')[:5]

            context = {
                'materias': materias,
                'carreras': Carrera.objects.all(),
                'noticias': noticias_profesor,
                'metricas': {
                    'total_alumnos': total_alumnos,
                    'promedio_grupal': 7.5, 
                    'tareas_pendientes': 12
                }
            }

            # Lógica extra para Jefe de Carrera (Carga de datos directa)
            if profesor.nivel == 'jefe de carrera':
                todos_profesores = Profesor.objects.all().select_related('user', 'carrera').prefetch_related('materias')
                lista_profesores = []
                for p in todos_profesores:
                    materias_ids = [m.id for m in p.materias.all()]
                    lista_profesores.append({
                        'obj': p, # Objeto completo por si acaso
                        'id': p.id,
                        'nombre': p.user.first_name + ' ' + p.user.last_name if p.user.first_name else p.user.username,
                        'email': p.user.email,
                        'nivel': p.nivel,
                        'carrera_id': p.carrera.id if p.carrera else '',
                        'carrera_nombre': p.carrera.nombre if p.carrera else 'Sin asignar',
                        'materias_ids_json': json.dumps(materias_ids),
                        'materias_count': len(materias_ids)
                    })
                context['lista_profesores'] = lista_profesores
                
                # Cargar todas las materias para el JS de filtrado local
                all_materias = list(Materia.objects.all().values('id', 'nombre', 'carrera_id', 'año'))
                context['all_materias_data'] = all_materias
            return render(request, 'profesor.html', context)
        except Profesor.DoesNotExist:
            return render(request, 'profesor.html', {'materias': [], 'metricas': {'total_alumnos': 0, 'promedio_grupal': 0, 'tareas_pendientes': 0}})
    
    # Lógica para el estudiante
    try:
        from datetime import datetime
        
        estudiante = request.user.estudiante
        
        # Obtener fecha y hora actual del servidor
        ahora = datetime.now()
        dia_actual = ahora.strftime('%A')  # Nombre del día en inglés
        hora_actual = ahora.time()
        
        # Mapeo de días en inglés a español
        dias_map = {
            'Monday': 'Lunes',
            'Tuesday': 'Martes',
            'Wednesday': 'Miércoles',
            'Thursday': 'Jueves',
            'Friday': 'Viernes',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        dia_espanol = dias_map.get(dia_actual, dia_actual)
        
        # Obtener todos los horarios del estudiante
        horario_completo = Horario.objects.filter(
            materia__carrera=estudiante.carrera,
            materia__año=estudiante.año
        ).select_related('materia').order_by('dia', 'hora_inicio')
        
        # Calcular si hay clase ahora y cuál es la próxima
        proxima_clase = None
        tiene_clase_ahora = False
        
        # Buscar clase actual (ahora mismo)
        clases_hoy = horario_completo.filter(dia=dia_espanol)
        for clase in clases_hoy:
            if clase.hora_inicio <= hora_actual <= clase.hora_fin:
                proxima_clase = clase
                tiene_clase_ahora = True
                break
        
        # Si no hay clase ahora, buscar la próxima clase de hoy
        if not tiene_clase_ahora:
            for clase in clases_hoy:
                if clase.hora_inicio > hora_actual:
                    proxima_clase = clase
                    break
        
        # Si no hay más clases hoy, buscar la primera clase del próximo día
        if not proxima_clase:
            # Orden de días de la semana
            orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            idx_hoy = orden_dias.index(dia_espanol) if dia_espanol in orden_dias else 0
            
            for i in range(1, 8):  # Buscar en los próximos 7 días
                siguiente_dia = orden_dias[(idx_hoy + i) % 7]
                proxima_clase = horario_completo.filter(dia=siguiente_dia).first()
                if proxima_clase:
                    break
        
        # Notas con tendencia
        notas_raw = Nota.objects.filter(estudiante=estudiante)[:3]
        notas = []
        for n in notas_raw:
            notas.append({
                'materia': n.materia,
                'valor': n.valor,
                'tendencia': n.tendencia,
                'porcentaje': n.valor * 20 # 5 * 20 = 100
            })
        
        # Noticias categorizadas
        noticias = Noticia.objects.filter(
            Q(visible_para='todos') | 
            (
                Q(visible_para='estudiantes') & 
                (Q(carrera=estudiante.carrera) | Q(carrera__isnull=True)) & 
                (Q(anio=estudiante.año) | Q(anio__isnull=True))
            )
        ).order_by('-fecha_publicacion')[:3]

        context = {
            'proxima_clase': proxima_clase,
            'tiene_clase_ahora': tiene_clase_ahora,
            'horario_completo': horario_completo,
            'notas': notas,
            'noticias': noticias
        }
        return render(request, 'estudiante.html', context)
    except Estudiante.DoesNotExist:
        return render(request, 'estudiante.html', {})

ROLE_MAP = {
    'profesor.com': 'profesor',
    'estudiante.com': 'estudiante',
    'jefedecarrera.com': 'jefedecarrera',
}

def determinar_rol_email(email):
    dominio = (email or '').lower().split('@')[-1]
    return ROLE_MAP.get(dominio, 'estudiante')

User = get_user_model()

@csrf_exempt
def register_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'method not allowed'}, status=405)
    data = json.loads(request.body.decode())
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if not (username and email and password):
        return JsonResponse({'success': False, 'error': 'missing fields'}, status=400)
    
    # Validar que el username no exista
    if User.objects.filter(username=username).exists():
        return JsonResponse({'success': False, 'error': 'Nombre de usuario ya en uso'}, status=400)
    
    # Validar que el email no exista
    if User.objects.filter(email=email).exists():
        return JsonResponse({'success': False, 'error': 'Correo electrónico ya registrado'}, status=400)

    user = User.objects.create_user(username=username, email=email, password=password)
    role = determinar_rol_email(email)

    # Validar carrera obligatoria
    carrera_id = data.get('carrera_id')
    if not carrera_id:
        user.delete()
        return JsonResponse({'success': False, 'error': 'Debe seleccionar una carrera'}, status=400)

    if role == 'estudiante':
        año = data.get('año')
        if not año:
            user.delete()
            return JsonResponse({'success': False, 'error': 'Debe seleccionar un año'}, status=400)
            
        try:
            carrera_obj = Carrera.objects.get(pk=carrera_id)
            Estudiante.objects.create(user=user, año=año, carrera=carrera_obj)
            profile_created = True
        except Carrera.DoesNotExist:
            user.delete()
            return JsonResponse({'success': False, 'error': 'Carrera no válida'}, status=400)
    
    else:  # profesor o jefedecarrera
        nivel = 'profesor'
        if role == 'jefedecarrera':
            nivel = 'jefe de carrera'
            
        try:
            carrera_obj = Carrera.objects.get(pk=carrera_id)
            Profesor.objects.create(user=user, carrera=carrera_obj, nivel=nivel)
            profile_created = True
        except Carrera.DoesNotExist:
            user.delete()
            return JsonResponse({'success': False, 'error': 'Carrera no válida'}, status=400)

    return JsonResponse({'success': True, 'role': role, 'profile_created': profile_created})

@csrf_exempt
def login_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'method not allowed'}, status=405)
    data = json.loads(request.body.decode())
    username_or_email = data.get('username')
    password = data.get('password')

    if not username_or_email or not password:
        return JsonResponse({'authenticated': False}, status=400)

    UserModel = get_user_model()
    # allow login by email or username
    if '@' in username_or_email:
        try:
            user_obj = UserModel.objects.get(email=username_or_email)
            username = user_obj.username
        except UserModel.DoesNotExist:
            return JsonResponse({'authenticated': False}, status=400)
    else:
        username = username_or_email

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        
        # Lógica de 'Recordar Sesión'
        remember = data.get('remember', False)
        if remember:
            request.session.set_expiry(1209600)  # 2 semanas (en segundos)
        else:
            request.session.set_expiry(0)  # Cerrar al cerrar navegador
            
        role = determinar_rol_email(user.email)
        return JsonResponse({'authenticated': True, 'role': role})
    return JsonResponse({'authenticated': False})

@csrf_exempt
@login_required
def crear_noticia_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if not request.user.is_profesor:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body.decode())
        titulo = data.get('titulo')
        contenido = data.get('contenido')
        visible_para = data.get('visible_para', 'estudiantes') # 'estudiantes', 'profesores', 'todos'
        categoria = data.get('categoria', 'aviso')
        carrera_id = data.get('carrera_id') # Puede ser null
        anio = data.get('año') # Puede ser null
        
        if not titulo or not contenido:
            return JsonResponse({'success': False, 'error': 'Título y contenido requeridos'}, status=400)
        
        profesor = request.user.profesor
        carrera_obj = Carrera.objects.get(id=carrera_id) if carrera_id else None

        Noticia.objects.create(
            titulo=titulo,
            contenido=contenido,
            autor=profesor,
            visible_para=visible_para,
            carrera=carrera_obj,
            anio=anio,
            categoria=categoria
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@login_required
def get_mis_noticias_api(request):
    print(f"DEBUG: Acceso a get_mis_noticias_api por {request.user.username}, Metodo: {request.method}")
    try:
        if not hasattr(request.user, 'profesor'):
            print(f"DEBUG: El usuario {request.user.username} NO tiene perfil de profesor.")
            return JsonResponse({'error': 'Perfil de profesor no encontrado'}, status=403)
            
        profesor = request.user.profesor
        print(f"DEBUG: Buscando noticias para profesor de carrera: {profesor.carrera}")
        # Filtro: noticias donde el autor es este profesor O son noticias de su carrera (para compatibilidad)
        noticias = Noticia.objects.filter(
            Q(autor=profesor) | 
            Q(carrera=profesor.carrera, autor__isnull=True)
        ).order_by('-fecha_publicacion')
        
        data = []
        for n in noticias:
            # Asegurar que los campos existen
            data.append({
                'id': n.id,
                'titulo': n.titulo or 'Sin título',
                'contenido': n.contenido or '',
                'fecha': n.fecha_publicacion.strftime('%d/%m/%Y %H:%M') if n.fecha_publicacion else '',
                'categoria': n.get_categoria_display().lower() if n.categoria else 'aviso'
            })
        return JsonResponse({'noticias': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required
def borrar_noticia_api(request, noticia_id):
    if request.method != 'DELETE' and request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        noticia = Noticia.objects.get(id=noticia_id)
        if noticia.autor and noticia.autor.user != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        noticia.delete()
        return JsonResponse({'success': True})
    except Noticia.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Noticia no encontrada'}, status=404)

@csrf_exempt
@login_required
def editar_noticia_api(request, noticia_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        noticia = Noticia.objects.get(id=noticia_id)
        if noticia.autor.user != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        data = json.loads(request.body.decode())
        noticia.titulo = data.get('titulo', noticia.titulo)
        noticia.contenido = data.get('contenido', noticia.contenido)
        noticia.categoria = data.get('categoria', noticia.categoria)
        noticia.visible_para = data.get('visible_para', noticia.visible_para)
        
        # Actualizar carrera y año si se proporcionan
        carrera_id = data.get('carrera_id')
        if carrera_id:
            try:
                noticia.carrera = Carrera.objects.get(id=carrera_id)
            except Carrera.DoesNotExist:
                pass
        else:
            noticia.carrera = None
            
        noticia.anio = data.get('anio') if data.get('anio') else None
        noticia.save()
        return JsonResponse({'success': True})
    except Noticia.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Noticia no encontrada'}, status=404)

@login_required
def subir_notas(request):
    """Vista para subir un archivo de notas en formato Excel
    Formato esperado: Nombre | Nota
    La materia, carrera y año se obtienen del formulario
    """
    if not request.user.is_profesor:
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')
        carrera_id = request.POST.get('carrera_id')
        anio = request.POST.get('anio')
        materia_id = request.POST.get('materia_id')
        
        if not archivo or not carrera_id or not anio or not materia_id:
            return JsonResponse({'error': 'Por favor completa todos los campos (archivo, carrera, año y materia)'})
        
        # Validar tipo de archivo
        if not archivo.name.endswith(('.xlsx', '.xls')):
            return JsonResponse({'error': 'Solo se aceptan archivos Excel (.xlsx o .xls)'})
        
        # Validar tamaño del archivo (máximo 5MB)
        if archivo.size > 5 * 1024 * 1024:
            return JsonResponse({'error': 'El archivo es demasiado grande. Máximo 5MB'})
        
        try:
            from django.conf import settings
            from django.db import transaction
            
            carrera = Carrera.objects.get(id=carrera_id)
            materia = Materia.objects.get(id=materia_id, carrera=carrera, año=anio)
            
            # Crear carpeta static/notas si no existe
            notas_dir = os.path.join(settings.BASE_DIR, 'static', 'notas')
            os.makedirs(notas_dir, exist_ok=True)
            
            # Guardar archivo con nombre único
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f'notas_{materia.nombre.replace(" ", "_")}_{carrera.nombre.replace(" ", "_")}_{anio}año_{timestamp}.xlsx'
            ruta_archivo = os.path.join(notas_dir, nombre_archivo)
            
            # Guardar el archivo
            with open(ruta_archivo, 'wb+') as destination:
                for chunk in archivo.chunks():
                    destination.write(chunk)
            
            # Procesar archivo Excel
            try:
                wb = openpyxl.load_workbook(ruta_archivo)
                sheet = wb.active
            except Exception as e:
                return JsonResponse({'error': f'Error al leer el archivo Excel: {str(e)}'})
            
            notas_creadas = 0
            notas_actualizadas = 0
            errores = []
            
            # Función para normalizar texto (eliminar tildes y convertir a minúsculas)
            def normalizar_texto(texto):
                import unicodedata
                # Eliminar tildes
                texto_sin_tildes = ''.join(
                    c for c in unicodedata.normalize('NFD', texto)
                    if unicodedata.category(c) != 'Mn'
                )
                # Convertir a minúsculas
                return texto_sin_tildes.lower().strip()
            
            # Procesar cada fila del Excel
            with transaction.atomic():
                # Saltar la primera fila (encabezados: Nombre, Nota)
                for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                    try:
                        # Validar que la fila tenga datos
                        if not row or all(cell is None for cell in row):
                            continue
                        
                        # Extraer datos de las columnas (solo 2 columnas ahora)
                        nombre_completo = str(row[0]).strip() if row[0] else None  # Columna A: Nombre
                        nota_valor = row[1]                                         # Columna B: Nota
                        
                        # Validar que todos los campos estén presentes
                        if not all([nombre_completo, nota_valor is not None]):
                            errores.append(f'Fila {row_idx}: Datos incompletos')
                            continue
                        
                        # Convertir y validar la nota
                        try:
                            nota_valor = float(nota_valor)
                            if nota_valor < 0 or nota_valor > 5:
                                errores.append(f'Fila {row_idx}: La nota debe estar entre 0 y 5')
                                continue
                        except (ValueError, TypeError):
                            errores.append(f'Fila {row_idx}: Nota inválida "{nota_valor}"')
                            continue
                        
                        # Buscar el estudiante por username únicamente
                        nombre_normalizado = normalizar_texto(nombre_completo)
                        estudiante = None
                        
                        # Buscar entre todos los estudiantes de la carrera y año
                        estudiantes_candidatos = Estudiante.objects.filter(
                            carrera=carrera,
                            año=anio
                        ).select_related('user')
                        
                        for est in estudiantes_candidatos:
                            username_bd = normalizar_texto(est.user.username or '')
                            
                            # Comparar solo por username normalizado
                            if nombre_normalizado == username_bd:
                                estudiante = est
                                break
                        
                        if not estudiante:
                            errores.append(f'Fila {row_idx}: Estudiante "{nombre_completo}" no encontrado en {carrera.nombre} - {anio}º año')
                            continue
                        
                        # Obtener nota anterior para calcular tendencia
                        nota_anterior = None
                        try:
                            nota_existente = Nota.objects.get(estudiante=estudiante, materia=materia)
                            nota_anterior = nota_existente.valor
                        except Nota.DoesNotExist:
                            pass
                        
                        # Calcular tendencia
                        tendencia = 'mantuvo'
                        if nota_anterior is not None:
                            if nota_valor > nota_anterior:
                                tendencia = 'subio'
                            elif nota_valor < nota_anterior:
                                tendencia = 'bajo'
                        
                        # Crear o actualizar la nota
                        nota, created = Nota.objects.update_or_create(
                            estudiante=estudiante,
                            materia=materia,
                            defaults={
                                'valor': nota_valor,
                                'tendencia': tendencia
                            }
                        )
                        
                        if created:
                            notas_creadas += 1
                        else:
                            notas_actualizadas += 1
                            
                    except Exception as e:
                        errores.append(f'Fila {row_idx}: Error inesperado - {str(e)}')
                        continue
            
            # Preparar mensaje de respuesta
            if notas_creadas == 0 and notas_actualizadas == 0:
                return JsonResponse({
                    'error': f'No se procesaron notas. Errores encontrados: {len(errores)}',
                    'detalles': errores[:10],  # Mostrar solo los primeros 10 errores
                    'archivo_guardado': nombre_archivo
                })
            
            mensaje = f'Procesamiento completado: {notas_creadas} notas creadas, {notas_actualizadas} notas actualizadas para {materia.nombre}'
            if errores:
                mensaje += f'. Se encontraron {len(errores)} errores'
            
            # Eliminar el archivo Excel después de procesarlo
            try:
                if os.path.exists(ruta_archivo):
                    os.remove(ruta_archivo)
            except Exception as e:
                pass  # Si no se puede eliminar, continuar sin error
            
            return JsonResponse({
                'exito': mensaje,
                'detalles': {
                    'creadas': notas_creadas,
                    'actualizadas': notas_actualizadas,
                    'materia': materia.nombre,
                    'errores': errores[:10] if errores else []  # Primeros 10 errores
                }
            })
            
        except Carrera.DoesNotExist:
            return JsonResponse({'error': 'Carrera no encontrada'})
        except Materia.DoesNotExist:
            return JsonResponse({'error': 'Materia no encontrada para la carrera y año seleccionados'})
        except ImportError:
            return JsonResponse({'error': 'La librería openpyxl no está instalada. Contacta al administrador.'})
        except Exception as e:
            import traceback
            return JsonResponse({'error': f'Error al procesar el archivo: {str(e)}', 'trace': traceback.format_exc()})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
def get_materias_api(request):
    """API para obtener materias filtradas por carrera y año"""
    try:
        carrera_id = request.GET.get('carrera_id')
        anio = request.GET.get('anio')
        
        if not carrera_id or not anio:
            return JsonResponse({'materias': []})
        
        materias = Materia.objects.filter(
            carrera_id=carrera_id,
            año=anio
        ).values('id', 'nombre')
        
        return JsonResponse({'materias': list(materias)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required
def asignar_profesor_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    # Verificar permisos (solo jefe de carrera)
    if not hasattr(request.user, 'profesor') or request.user.profesor.nivel != 'jefe de carrera':
        return JsonResponse({'error': 'No tienes permisos para realizar esta acción'}, status=403)
        
    try:
        data = json.loads(request.body)
        profesor_id = data.get('profesor_id')
        carrera_id = data.get('carrera_id')
        materias_ids = data.get('materias_ids', [])
        
        if not profesor_id:
            return JsonResponse({'error': 'Falta ID de profesor'})
            
        profesor = Profesor.objects.get(id=profesor_id)
        
        # Asignar Carrera
        if carrera_id:
            profesor.carrera_id = carrera_id
        else:
            profesor.carrera = None
        profesor.save()
        
        # Asignar Materias (ManyToManyField)
        # Aseguramos que los IDs sean enteros y existan
        if materias_ids:
             materias_ids = [int(m_id) for m_id in materias_ids]
             profesor.materias.set(materias_ids)
        else:
             profesor.materias.clear()
        
        return JsonResponse({'success': True})
        
    except Profesor.DoesNotExist:
        return JsonResponse({'error': 'Profesor no encontrado'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def subir_horarios(request):
    """Vista para subir horarios desde archivo Excel
    Formato esperado: Materia | Día | Hora Inicio | Hora Fin
    """
    if not request.user.is_profesor:
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    
    if request.user.profesor.nivel != 'jefe de carrera':
        return JsonResponse({'error': 'Solo los jefes de carrera pueden subir horarios'}, status=403)
    
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')
        carrera_id = request.POST.get('carrera_id')
        anio = request.POST.get('anio')
        reemplazar = request.POST.get('reemplazar') == 'true'
        
        if not archivo or not carrera_id or not anio:
            return JsonResponse({'error': 'Por favor completa todos los campos'})
        
        if not archivo.name.endswith(('.xlsx', '.xls')):
            return JsonResponse({'error': 'Solo se aceptan archivos Excel'})
        
        if archivo.size > 5 * 1024 * 1024:
            return JsonResponse({'error': 'Archivo demasiado grande (máx 5MB)'})
        
        try:
            from django.conf import settings
            from django.db import transaction
            from datetime import datetime, time
            
            carrera = Carrera.objects.get(id=carrera_id)
            temp_dir = os.path.join(settings.BASE_DIR, 'static', 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f'horario_{carrera.nombre.replace(" ", "_")}_{anio}_{timestamp}.xlsx'
            ruta_archivo = os.path.join(temp_dir, nombre_archivo)
            
            with open(ruta_archivo, 'wb+') as destination:
                for chunk in archivo.chunks():
                    destination.write(chunk)
            
            try:
                import openpyxl
                wb = openpyxl.load_workbook(ruta_archivo)
                sheet = wb.active
            except Exception as e:
                return JsonResponse({'error': f'Error al leer Excel: {str(e)}'})
            
            horarios_creados = 0
            horarios_actualizados = 0
            errores = []
            
            def normalizar_texto(texto):
                import unicodedata
                texto_sin_tildes = ''.join(
                    c for c in unicodedata.normalize('NFD', texto)
                    if unicodedata.category(c) != 'Mn'
                )
                return texto_sin_tildes.lower().strip()
            
            def parsear_hora(valor):
                if isinstance(valor, time):
                    return valor
                if isinstance(valor, str):
                    try:
                        partes = valor.strip().split(':')
                        if len(partes) == 2:
                            return time(int(partes[0]), int(partes[1]))
                    except:
                        pass
                return None
            
            if reemplazar:
                materias_carrera = Materia.objects.filter(carrera=carrera, año=anio)
                Horario.objects.filter(materia__in=materias_carrera).delete()
            
            with transaction.atomic():
                for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                    try:
                        if not row or all(cell is None for cell in row):
                            continue
                        
                        nombre_materia = str(row[0]).strip() if row[0] else None
                        dia = str(row[1]).strip() if row[1] else None
                        hora_inicio_raw = row[2]
                        hora_fin_raw = row[3]
                        aula = str(row[4]).strip() if len(row) > 4 and row[4] else None
                        
                        if not all([nombre_materia, dia, hora_inicio_raw, hora_fin_raw]):
                            errores.append(f'Fila {row_idx}: Datos incompletos')
                            continue
                        
                        hora_inicio = parsear_hora(hora_inicio_raw)
                        hora_fin = parsear_hora(hora_fin_raw)
                        
                        if not hora_inicio or not hora_fin:
                            errores.append(f'Fila {row_idx}: Formato de hora inválido')
                            continue
                        
                        if hora_fin <= hora_inicio:
                            errores.append(f'Fila {row_idx}: Hora fin debe ser mayor que inicio')
                            continue
                        
                        dias_validos = ['lunes', 'martes', 'miércoles', 'miercoles', 'jueves', 'viernes', 'sábado', 'sabado', 'domingo']
                        dia_normalizado = normalizar_texto(dia)
                        if dia_normalizado not in dias_validos:
                            errores.append(f'Fila {row_idx}: Día inválido')
                            continue
                        
                        dia_capitalizado = dia.capitalize()
                        nombre_normalizado = normalizar_texto(nombre_materia)
                        materia = None
                        
                        materias_candidatas = Materia.objects.filter(carrera=carrera, año=anio)
                        for m in materias_candidatas:
                            if normalizar_texto(m.nombre) == nombre_normalizado:
                                materia = m
                                break
                        
                        if not materia:
                            errores.append(f'Fila {row_idx}: Materia "{nombre_materia}" no encontrada')
                            continue
                        
                        horario, created = Horario.objects.update_or_create(
                            materia=materia,
                            dia=dia_capitalizado,
                            hora_inicio=hora_inicio,
                            defaults={'hora_fin': hora_fin, 'aula': aula}
                        )
                        
                        if created:
                            horarios_creados += 1
                        else:
                            horarios_actualizados += 1
                            
                    except Exception as e:
                        errores.append(f'Fila {row_idx}: {str(e)}')
                        continue
            
            try:
                if os.path.exists(ruta_archivo):
                    os.remove(ruta_archivo)
            except:
                pass
            
            if horarios_creados == 0 and horarios_actualizados == 0:
                return JsonResponse({
                    'error': f'No se procesaron horarios. Errores: {len(errores)}',
                    'detalles': errores[:10]
                })
            
            mensaje = f'{horarios_creados} creados, {horarios_actualizados} actualizados'
            if errores:
                mensaje += f'. {len(errores)} errores'
            
            return JsonResponse({
                'exito': mensaje,
                'detalles': {
                    'creados': horarios_creados,
                    'actualizados': horarios_actualizados,
                    'errores': errores[:10] if errores else []
                }
            })
            
        except Carrera.DoesNotExist:
            return JsonResponse({'error': 'Carrera no encontrada'})
        except Exception as e:
            import traceback
            return JsonResponse({'error': f'Error: {str(e)}', 'trace': traceback.format_exc()})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def obtener_estudiantes_notas_api(request, materia_id):
    """API para obtener estudiantes y sus notas de una materia específica"""
    try:
        # Verificar que el usuario sea profesor
        if not request.user.is_profesor:
            return JsonResponse({'error': 'Acceso denegado'}, status=403)
        
        # Obtener la materia
        try:
            materia = Materia.objects.get(id=materia_id)
        except Materia.DoesNotExist:
            return JsonResponse({'error': 'Materia no encontrada'}, status=404)
        
        # Obtener todos los estudiantes de la carrera y año de la materia
        estudiantes = Estudiante.objects.filter(
            carrera=materia.carrera,
            año=materia.año
        ).select_related('user').order_by('user__username')
        
        # Crear lista de estudiantes con sus notas
        estudiantes_data = []
        for estudiante in estudiantes:
            # Buscar si tiene nota en esta materia
            try:
                nota = Nota.objects.get(estudiante=estudiante, materia=materia)
                nota_valor = nota.valor
                tendencia = nota.tendencia
            except Nota.DoesNotExist:
                nota_valor = None
                tendencia = None
            
            estudiantes_data.append({
                'id': estudiante.id,
                'nombre': estudiante.user.username,
                'nota': nota_valor,
                'tendencia': tendencia
            })
        
        return JsonResponse({
            'estudiantes': estudiantes_data,
            'materia': materia.nombre
        })
        
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'trace': traceback.format_exc()}, status=500)
