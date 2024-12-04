
from collections import defaultdict,Counter
from django.forms import ValidationError
import joblib
from django.shortcuts import render, redirect
from .models import DatosAgricultura, Recomendacion, reportes  # Asegúrate de importar tu modelo
from .models import User
from django.contrib import messages
import numpy as np
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
# Cargar los modelos y el escalador una vez al inicio del archivo
rf_model = joblib.load('random_forest_model.joblib')
scaler = joblib.load('scaler.joblib')

from django.shortcuts import render
from django.contrib import messages
import numpy as np
from .models import DatosAgricultura

def index_view(request):
    estimated_rendimiento = None  # Inicializar la variable

    if request.method == 'POST':
        try:
            # Obtener datos del formulario y convertir a float
            Temp_Max = float(request.POST.get('Temp_Max'))
            Temp_Min = float(request.POST.get('Temp_Min'))
            Humedad = float(request.POST.get('Humedad'))
            Radiacion_Solar = float(request.POST.get('Radiacion_Solar'))
            Viento = float(request.POST.get('Viento'))
            Precipitacion = float(request.POST.get('Precipitacion'))
            pH_Suelo = float(request.POST.get('pH_Suelo'))
            Nitrogeno = float(request.POST.get('Nitrogeno'))
            Fertilizacion = float(request.POST.get('Fertilizacion'))
            Densidad = float(request.POST.get('Densidad'))
            N_Flores = int(request.POST.get('N_Flores'))  # Cambiar a int ya que es IntegerField
            Plagas = int(request.POST.get('Plagas'))  # Cambiar a int ya que es IntegerField
            Caida_Frutos = float(request.POST.get('Caida_Frutos'))
            nhectaria = float(request.POST.get('nhectaria'))  # Obtener el número de hectáreas
            tiempo_pro = float(request.POST.get('tiempo_pro'))  # Obtener el tiempo transcurrido
        except (ValueError, TypeError):
            messages.error(request, "Error al procesar los datos del formulario. Asegúrese de que todos los campos son válidos.")
            return render(request, 'index.html', {'estimated_rendimiento': estimated_rendimiento})

        # Crear un array con las características para la predicción
        features = np.array([[Temp_Max, Temp_Min, Humedad, Radiacion_Solar,
                              Viento, Precipitacion, pH_Suelo, Nitrogeno,
                              Fertilizacion, Densidad, N_Flores,
                              Plagas, Caida_Frutos]])

        # Escalar las características
        scaled_features = scaler.transform(features)

        # Realizar la predicción
        estimated_rendimiento = rf_model.predict(scaled_features)[0]

        # Obtener el ID del usuario de la sesión
        user_id = request.session.get('user_id')  # Recuperar el ID del usuario de la sesión

        if user_id:  # Verificar si el ID del usuario está disponible
            try:
                # Crear un nuevo registro en la base de datos
                agricultura = DatosAgricultura(
                    pkuser_id=user_id,  # Guardar el ID del usuario en pkuser
                    Temp_Max=Temp_Max,
                    Temp_Min=Temp_Min,
                    Humedad=Humedad,
                    Radiacion_Solar=Radiacion_Solar,
                    Viento=Viento,
                    Precipitacion=Precipitacion,
                    pH_Suelo=pH_Suelo,
                    Nitrogeno=Nitrogeno,
                    Fertilizacion=Fertilizacion,
                    Densidad=Densidad,
                    N_Flores=N_Flores,
                    Plagas=Plagas,
                    Caida_Frutos=Caida_Frutos,
                    Rendimiento=estimated_rendimiento,  # Guardar rendimiento estimado
                    nhectaria=nhectaria,  # Guardar el número de hectáreas
                    tiempo_pro=tiempo_pro  # Guardar el tiempo transcurrido
                )
                agricultura.save()

                # Mensaje de éxito con rendimiento estimado
                messages.success(request, f'Rendimiento estimado: {estimated_rendimiento:.2f} Kg/ha')
            except (ValueError, TypeError):
                messages.error(request, "Error al procesar los datos de nhectarias o tiempo transcurrido.")
        else:
            messages.warning(request, "No se ha encontrado el ID del usuario. No se puede guardar el registro.")

    # Inicializar latest_record
    latest_record = None

    # Verificación de autenticación
    user_id = request.session.get('user_id')  # Obtener el ID del usuario de la sesión
    if user_id:
        # Obtener el último registro guardado
        latest_record = DatosAgricultura.objects.filter(pkuser_id=user_id).order_by('-id').first()
        if latest_record:
            messages.info(request, f'Último registro encontrado: {latest_record.Rendimiento:.2f} Kg/ha')
        else:
            messages.warning(request, 'No hay registros disponibles para este usuario.')
    else:
        messages.warning(request, "No estás autenticado. Por favor, inicia sesión para ver tus registros.")

    return render(request, 'index.html', {
        'estimated_rendimiento': estimated_rendimiento,
        'latest_record': latest_record  # Pasar el último registro a la plantilla
    })


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(f'Documento ingresado: {email}')
        print(f'Contraseña ingresada: {password}')

        try:
            # Intentar obtener el usuario por su email
            user = User.objects.get(email=email)
            print(f'Usuario encontrado: {user.name}')  # Verificar que se encontró el usuario

            # Verificar la contraseña
            if check_password(password, user.password):  # Verificación segura
                # Aquí puedes acceder al ID del usuario
                user_id = user.id
                print(f'ID del usuario: {user_id}')

                # Iniciar sesión (puedes usar tu propia lógica de sesión)
                request.session['user_id'] = user_id  # Almacena el ID en la sesión
                return redirect('index')  # Redirige a la página de inicio después de iniciar sesión
            else:
                messages.error(request, 'Credenciales incorrectas')
        except User.DoesNotExist:
            messages.error(request, 'Credenciales incorrectas')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión con éxito.')
    return redirect('login')


def reporte(request):
    user_id = request.session.get('user_id')

    # Verificar si el usuario está autenticado
    if user_id is None:
        messages.error(request, 'No estás autenticado. Por favor, inicia sesión para acceder a los reportes.')
        return redirect('/accounts/login/')

    # Obtener el número de hectáreas del formulario, si se proporciona
    nhectarias_filter = request.GET.get('nhectarias', None)

    # Obtener el rango de fechas del formulario, si se proporciona
    fecha_inicio = request.GET.get('fecha_inicio', None)
    fecha_fin = request.GET.get('fecha_fin', None)

    # Filtrar los datos agrícolas del usuario autenticado
    try:
        # Construir la consulta base
        query = DatosAgricultura.objects.filter(pkuser_id=user_id)

        # Aplicar filtros por hectárea y fechas, si se proporcionan
        if nhectarias_filter:
            query = query.filter(nhectaria=nhectarias_filter)
        
        if fecha_inicio and fecha_fin:
            query = query.filter(created__range=[fecha_inicio, fecha_fin])

        # Obtener los datos filtrados
        datos_agricultura = list(query)

        # Preparar datos para los gráficos
        temperaturas_maximas = [dato.Temp_Max for dato in datos_agricultura]
        temperaturas_minimas = [dato.Temp_Min for dato in datos_agricultura]
        rendimientos = [dato.Rendimiento for dato in datos_agricultura]
        humedades = [dato.Humedad for dato in datos_agricultura]
        precipitaciones = [dato.Precipitacion for dato in datos_agricultura]
        radiaciones = [dato.Radiacion_Solar for dato in datos_agricultura]
        fechas = [dato.created.strftime("%Y-%m-%d") for dato in datos_agricultura]
        hectarias = [dato.nhectaria for dato in datos_agricultura]

        # Contar el número de predicciones por hectárea y sumar el rendimiento
        predicciones_counts = Counter(hectarias)
        rendimiento_por_hectaria = defaultdict(float)

        for dato in datos_agricultura:
            rendimiento_por_hectaria[dato.nhectaria] += dato.Rendimiento

        hectarias_labels = list(predicciones_counts.keys())
        predicciones_values = list(predicciones_counts.values())
        rendimiento_totales = [rendimiento_por_hectaria[label] for label in hectarias_labels]

        # Calcular el rendimiento total
        rendimiento_total = sum(rendimiento_totales)

        return render(request, 'reporte.html', {
            'datos_agricultura': datos_agricultura,
            'temperaturas_maximas': temperaturas_maximas,
            'temperaturas_minimas': temperaturas_minimas,
            'rendimientos': rendimientos,
            'humedades': humedades,
            'precipitaciones': precipitaciones,
            'radiaciones': radiaciones,
            'fechas': fechas,
            'hectarias': hectarias,
            'nhectarias_filter': nhectarias_filter,
            'hectarias_labels': hectarias_labels,  # Para el nuevo gráfico
            'predicciones_counts': predicciones_values,  # Para el nuevo gráfico
            'rendimiento_totales': rendimiento_totales,  # Sumatoria del rendimiento por hectárea
            'rendimiento_total': rendimiento_total,  # Rendimiento total
        })

    except DatosAgricultura.DoesNotExist:
        messages.error(request, 'No se encontraron datos agrícolas para el usuario.')
        return redirect('/')

    except Exception as e:
        messages.error(request, f'Ocurrió un error: {str(e)}')
        return redirect('/')



def latest_record_view(request):
    # Obtener el último registro guardado
    latest_record = DatosAgricultura.objects.order_by('-id').first()  # Ordenar por ID descendente y obtener el primero

    return render(request, 'latest_record.html', {'latest_record': latest_record})

def save_recomendaciones_view(request):
    user_id = request.session.get('user_id')
    print(f'User ID en sesión: {user_id}')  # Para depuración

    if user_id is None:
        messages.error(request, 'No estás autenticado. Por favor, inicia sesión para guardar recomendaciones.')
        return redirect('/login/')  # Redirigir a la página de inicio de sesión

    if request.method == 'POST':
        # Obtener el ID del reporte desde el formulario (si existe)
        reporte_id = request.POST.get('reporte_id')
        print(f'ID del reporte recibido: {reporte_id}')  # Para depuración

        try:
            if reporte_id:
                # Intenta obtener el reporte existente
                report_record = reportes.objects.get(id=reporte_id)
            else:
                # Si no se proporciona un ID, crea un nuevo reporte
                latest_data = DatosAgricultura.objects.filter(pkuser_id=user_id).order_by('-id').first()
                if not latest_data:
                    messages.error(request, 'No hay datos agrícolas disponibles para crear un reporte.')
                    return render(request, 'index.html')

                # Crear un nuevo reporte
                report_record = reportes.objects.create(
                    pkdatos=latest_data,
                    pkuser_id=user_id
                )
                messages.success(request, 'Nuevo reporte creado.')

            # Obtener valores del formulario
            rclimaticas = request.POST.get('rclimaticas')
            rsuelo = request.POST.get('rsuelo')
            ragronomicas = request.POST.get('ragronomicas')
            rfenologicos = request.POST.get('rfenologicos')
            rplagas = request.POST.get('rplagas')

            # Comprobar que todos los campos estén llenos
            if not all([rclimaticas, rsuelo, ragronomicas, rfenologicos, rplagas]):
                messages.error(request, 'Todos los campos son obligatorios.')
                return render(request, 'index.html')

            # Crear la recomendación
            recomendacion = Recomendacion(
                reporte=report_record,
                rclimaticas=rclimaticas,
                rsuelo=rsuelo,
                ragronomicas=ragronomicas,
                rfenologicos=rfenologicos,
                rplagas=rplagas
            )
            recomendacion.save()
            messages.success(request, 'Recomendaciones guardadas correctamente.')
            return redirect('index')  # Redirigir a la página principal o a donde desees

        except reportes.DoesNotExist:
            messages.error(request, 'El reporte especificado no existe.')
        except Exception as e:
            messages.error(request, f'Error al guardar recomendaciones: {str(e)}')
            print(f'Error al guardar: {e}')  # Para ver el error en la consola

    return render(request, 'index.html')  # Cambiar por el nombre de tu plantilla

def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Aquí puedes agregar validaciones adicionales si es necesario

        # Cifrar la contraseña antes de guardar el usuario
        hashed_password = make_password(password)

        # Guarda el usuario en la base de datos
        user = User(name=name, email=email, password=hashed_password)
        user.save() #Se guarda la nueva instancia

        messages.success(request, 'Usuario creado exitosamente!')
        return redirect('login')  # Redirige a la página de login

    return render(request, 'register.html')
# def register_view(request):
#     return render(request,"register.html")#

def reset_view(request):
    return render(request,"reset.html")

import uuid
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password 

def recuperar(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Busca al usuario por el correo electrónico
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'reset.html', {'error': 'El correo electrónico no está registrado.'})

        # Generar un token único
        token = uuid.uuid4()
        user.token = token
        user.token_expires = timezone.now() + timedelta(hours=1)  # Establecer la expiración
        user.save()  # Guardar el usuario con el nuevo token

        # Enviar el correo electrónico
        reset_link = f"http://localhost:8000/restablecer/{token}/"
        send_mail(
            'Recuperación de Contraseña',
            f'Haz clic en el siguiente enlace para restablecer tu contraseña: {reset_link}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        success = 'Se ha enviado un correo con instrucciones para restablecer tu contraseña.'
        return render(request, 'reset.html', {'success': success})

    return render(request, 'reset.html')

def restablecer(request, token):
    try:
        user = User.objects.get(token=token)
    except User.DoesNotExist:
        return render(request, 'restablecer.html', {'error': 'Token inválido.'})

    # Verificar si el token ha expirado
    if not user.is_token_valid():
        return render(request, 'restablecer.html', {'error': 'El token ha expirado.'})

    if request.method == 'POST':
        nueva_contraseña = request.POST.get('nueva_contraseña')
        confirmar_contraseña = request.POST.get('confirmar_contraseña')

        if nueva_contraseña != confirmar_contraseña:
            return render(request, 'restablecer.html', {'error': 'Las contraseñas no coinciden.'})

        user.password = make_password(nueva_contraseña)  # Cifrar la nueva contraseña
        user.token = None  # Limpiar el token después de usarlo
        user.token_expires = None  # Limpiar la expiración
        user.save()
        success = 'Tu contraseña ha sido restablecida con éxito.'
        return render(request, 'restablecer.html', {'success': success})

    return render(request, 'restablecer.html', {'email': user.email})