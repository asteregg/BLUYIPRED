
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

def index_view(request): #Función
    estimated_rendimiento = None  # Inicializar la variable con un valor null

    if request.method == 'POST':
        # Obtener datos del formulario
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
        N_Flores = float(request.POST.get('N_Flores'))
        Caida_Frutos = float(request.POST.get('Caida_Frutos'))
        Plagas = float(request.POST.get('Plagas'))

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
            # Crear un nuevo registro en la base de datos
            agricultura = DatosAgricultura(
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
                Caida_Frutos=Caida_Frutos,
                Plagas=Plagas,
                Rendimiento=estimated_rendimiento,  # Guardar rendimiento estimado
                pkuser_id=user_id  # Guardar el ID del usuario en pkuser
            )
            agricultura.save()

            # Mensaje de éxito con rendimiento estimado
            messages.success(request, f'Rendimiento estimado: {estimated_rendimiento:.2f} Kg/ha')

    # Inicializar latest_record
    latest_record = None

    # Verificación de autenticación
    user_id = request.session.get('user_id')  # Obtener el ID del usuario de la sesión
    if user_id:
        # Obtener el último registro guardado
        latest_record = DatosAgricultura.objects.filter(pkuser_id=user_id).order_by('-id').first()

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
    # Obtener el ID del usuario de la sesión
    user_id = request.session.get('user_id')
    print(f'User ID en sesión: {user_id}')   # Para depuración

    # Verificar que se haya obtenido un ID de usuario
    if user_id is None:
        # Si no hay ID de usuario en la sesión, agregar un mensaje de error
        messages.error(request, 'No estás autenticado. Por favor, inicia sesión para acceder a los reportes.')
        return redirect('/accounts/login/')  # Redirigir a la página de inicio de sesión

    # Obtener todos los datos agrícolas del usuario autenticado
    datos_agricultura = DatosAgricultura.objects.filter(pkuser_id=user_id)

    # Pasar los datos a la plantilla
    return render(request, 'reporte.html', {'datos_agricultura': datos_agricultura})

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