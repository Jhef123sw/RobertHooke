import matplotlib
import zipfile
matplotlib.use('Agg')  # Forzar backend sin GUI
import matplotlib.pyplot as plt
import base64
import os
import io
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, FileResponse, Http404
from django.contrib import messages
from datetime import datetime
import pandas as pd
import shutil
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Estudiante, Reporte, Asistencia
from .forms import EstudianteForm, CargarExcelForm, LoginForm, EstudianteForm2, CargarExcelFormReporte
from .backends import EstudianteBackend
from .decorators import estudiante_tipo_requerido
from django.core.paginator import Paginator
from django.db.models import Q
import os
import matplotlib.pyplot as plt
import math
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from .models import Reporte, Estudiante
from datetime import datetime

#Descargas
@login_required
def descargar_reporte(request):
    usuario_actual = request.user
    try:
        ruta_descarga = f"media/reportes/simulacros/{usuario_actual.usuario}_reporte_simulacro.png"
        if not os.path.exists(ruta_descarga):
            raise Http404("El reporte no se ha generado todavía, por favor ponte en contacto con la administración.")
        
        
        return FileResponse(open(ruta_descarga, 'rb'), as_attachment=True, filename=os.path.basename(ruta_descarga))

    except Exception as e:
        print(f"Error al descargar el reporte: {e}")
        raise Http404("No se pudo descargar el reporte.")
    
@login_required
@estudiante_tipo_requerido(['administrador'])
def descargar_reportes_zip(request):
    # Ruta a la carpeta de simulacros
    carpeta = os.path.join(settings.MEDIA_ROOT, "reportes", "simulacros")
    
    if not os.path.exists(carpeta):
        raise Http404("La carpeta de reportes no existe")

    # Creamos el archivo ZIP en memoria
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for nombre_archivo in os.listdir(carpeta):
            ruta_archivo = os.path.join(carpeta, nombre_archivo)
            if os.path.isfile(ruta_archivo):
                zip_file.write(ruta_archivo, arcname=nombre_archivo)

    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="reportes_simulacros.zip"'
    return response

@login_required
@estudiante_tipo_requerido(['administrador'])
def descargar_reportes_asistencia_zip(request):
    # Ruta a la carpeta de asistenicias
    carpeta = os.path.join(settings.MEDIA_ROOT, "reportes", "asistencias")
    
    if not os.path.exists(carpeta):
        raise Http404("La carpeta de reportes no existe, comuníquese con soporte")

    # Creamos el archivo ZIP en memoria
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for nombre_archivo in os.listdir(carpeta):
            ruta_archivo = os.path.join(carpeta, nombre_archivo)
            if os.path.isfile(ruta_archivo):
                zip_file.write(ruta_archivo, arcname=nombre_archivo)

    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="reportes_asistencias.zip"'
    return response


#Generación/cración de imágenes/reportes

def generar_reporte_asistencia_todos(request):
    try:
        estudiantes = Estudiante.objects.all()
        for estudiante in estudiantes:
            asistencia = estudiante.asistencia.all().order_by('Fecha')
            generar_reporte_asistencia_imagen(estudiante, asistencia)
        messages.success(request, "Gráficos y reportes generados exitosamente para todos los estudiantes.")
        return redirect('seleccionar_fecha_generacion')
    except Exception as e:
        print(f"Error al generar todo el reporte: {e}")
        raise Http404("Ocurrió un error al generar los reportes.")



def generar_reporte_asistencia_imagen(estudiante, asistencias):
    
    plantilla_path = os.path.join(settings.MEDIA_ROOT, "D:/RobertHooke/login/static/img/plantilla-asistencia.png")  # Asegúrate de que esta plantilla exista
    imagen = Image.open(plantilla_path)
    draw = ImageDraw.Draw(imagen)

    try:
        fuente_titulo = ImageFont.truetype("arial.ttf", 28)
        fuente_texto = ImageFont.truetype("arial.ttf", 22)
    except:
        fuente_titulo = ImageFont.load_default()
        fuente_texto = ImageFont.load_default()

    posiciones_x = {
        "usuario": 88,
        "nombre": 185,
        "Fecha_Asistencia": 602,
        "Ingreso_mana": 740,
        "Salida_mana": 820,
        "Ingreso_tarde": 915,
        "Salida_tarde": 995,
        "Ingreso_noche": 1085,
        "Salida_noche": 1165,
        "Observacion": 1250,
    }

    b = 300
    for asistencia in asistencias:
        fila = {
            "usuario": estudiante.usuario,
            "nombre": estudiante.nombre,
            "Fecha_Asistencia": asistencia.Fecha.strftime('%d/%m/%Y'),
            "Ingreso_mana": asistencia.Ingreso_mana,
            "Salida_mana": asistencia.Salida_mana,
            "Ingreso_tarde": asistencia.Ingreso_tarde,
            "Salida_tarde": asistencia.Salida_tarde,
            "Ingreso_noche": asistencia.Ingreso_noche,
            "Salida_noche": asistencia.Salida_noche,
            "Observacion": asistencia.Observacion,
        }
        for campo, x in posiciones_x.items():
            draw.text((x, b), str(fila[campo]), fill="black", font=fuente_texto)
        b += 45

    carpeta = f'media/reportes/asistencias'
    os.makedirs(carpeta, exist_ok=True)
    nombre_archivo = os.path.join(carpeta, f'reporte_asistencia_{estudiante.usuario}.png')
    imagen.save(nombre_archivo)

    return nombre_archivo

@login_required
def generar_reporte_asistencia(request):
    estudiante = request.user  # Asume que Estudiante es el modelo de usuario
    asistencias = Asistencia.objects.filter(KK_usuario=estudiante).order_by('Fecha')
    if not asistencias.exists():
        return render(request, "prueba.html")  # Puedes crear esta plantilla si deseas

    ruta_imagen = generar_reporte_asistencia_imagen(estudiante, asistencias)

    return FileResponse(open(ruta_imagen, 'rb'), as_attachment=True, filename=os.path.basename(ruta_imagen))





@login_required
@estudiante_tipo_requerido(['administrador'])
def generar_todo_reporte(request):
    try:
        estudiantes = Estudiante.objects.all()
        ruta_guardar = 'media/reportes/simulacros'
        plantilla_path = "D:/RobertHooke/login/static/img/plantilla-notas.png"

        if not os.path.exists(plantilla_path):
            raise Http404("No se encontró la plantilla del reporte.")

        # Definimos cursos y preguntas por nivel
        cursos_pre = [
            "Razonamiento Verbal", "Razonamiento Matemático", "Aritmética", "Álgebra",
            "Geometría", "Trigonometría", "Física", "Química", "Biología", "Lenguaje",
            "Literatura", "Historia", "Geografía", "Filosofía", "Psicología", "Economía"
        ]

        preguntas_pre = {
            "Razonamiento Verbal": 15,
            "Razonamiento Matemático": 15,
            "Aritmética": 5,
            "Álgebra": 5,
            "Geometría": 4,
            "Trigonometría": 4,
            "Física": 5,
            "Química": 5,
            "Biología": 9,
            "Lenguaje": 6,
            "Literatura": 6,
            "Historia": 3,
            "Geografía": 2,
            "Filosofía": 2,
            "Psicología": 2,
            "Economía": 2,
        }

        cursos_semillero = [
            "Razonamiento Verbal", "Razonamiento Matemático", "Aritmética", "Álgebra",
            "Geometría", "Trigonometría", "Física", "Química", "Biología", "Lenguaje",
            "Literatura", "Historia", "Geografía", "Filosofía", "Psicología", "Economía"
        ]

        preguntas_semillero = {
            "Razonamiento Verbal": 10,
            "Razonamiento Matemático": 10,
            "Aritmética": 5,
            "Álgebra": 5,
            "Geometría": 0,
            "Trigonometría": 0,
            "Física": 0,
            "Química": 0,
            "Biología": 0,
            "Lenguaje": 0,
            "Literatura": 5,
            "Historia": 0,
            "Geografía": 0,
            "Filosofía": 0,
            "Psicología": 0,
            "Economía": 0,
        }

        for estudiante in estudiantes:
            reportes = estudiante.reportes.all().order_by('fecha_de_examen')
            if not reportes.exists():
                continue

            ruta_carpeta = f'media/{estudiante.usuario}_2025/imagenes_reporte/'
            os.makedirs(ruta_carpeta, exist_ok=True)

            # 1. Generar gráficos por curso según nivel
            

            # 1. Recolectar datos por curso según nivel
            nivel = reportes.first().nivel  # Todos los reportes del estudiante tienen mismo nivel
            if nivel == "30":
                cursos = cursos_semillero
                preguntas_por_curso = preguntas_semillero
            else:
                cursos = cursos_pre
                preguntas_por_curso = preguntas_pre

            datos_por_curso = {curso: [] for curso in cursos}

            for reporte in reportes:
                datos_cursos = reporte.obtener_datos()
                fecha = reporte.fecha_de_examen

                for curso in cursos:
                    if curso not in datos_cursos:
                        continue
                    correctas, incorrectas = datos_cursos[curso]
                    total = preguntas_por_curso.get(curso, 10)

                    datos_por_curso[curso].append({
                        "Fecha Simulacro": fecha,
                        "correctas": correctas,
                        "incorrectas": incorrectas,
                        "total": total
                    })

            # 2. Generar gráfico por curso con función externa
            for curso, datos in datos_por_curso.items():
                crear_grafico_estudiante_curso(estudiante, curso, datos)


            # 2. Gráfico de puntajes por fecha
            fechas = [r.fecha_de_examen.strftime('%Y-%m-%d') for r in reportes]
            puntajes = [r.obtener_total_puntaje() for r in reportes]

            def generar_grafico_puntaje_barras(x, y):
                fig, ax = plt.subplots(figsize=(6, 3))
                barras = ax.bar(x, y, color='#DA880B')
                for spine in ax.spines.values():
                    spine.set_visible(False)
                ax.set_title("")
                ax.set_xlabel("")
                ax.set_ylabel("")
                for barra, valor in zip(barras, y):
                    altura = barra.get_height()
                    ax.text(barra.get_x() + barra.get_width() / 2, altura + 1, f'{valor}',
                            ha='center', va='bottom', fontsize=20, fontweight='bold')
                tamaño_letra = 10 if len(x) > 5 else 10
                plt.xticks(rotation=0, fontsize=tamaño_letra)
                ax.tick_params(axis='y', left=False, labelleft=False)
                ax.grid(False)
                ruta_grafico = os.path.join(ruta_carpeta, "zgrafico_puntaje.png")
                fig.tight_layout()
                fig.savefig(ruta_grafico, bbox_inches='tight')
                plt.close(fig)
                return ruta_grafico

            ruta_grafico_puntaje = generar_grafico_puntaje_barras(fechas, puntajes)

            # 3. Crear imagen final con todos los gráficos
            plantilla = Image.open(plantilla_path)
            draw = ImageDraw.Draw(plantilla)
            fuente = ImageFont.truetype("arial.ttf", 40)
            draw.text((720, 124), estudiante.nombre, fill="black", font=fuente)

            a, b, i = 180, 210, 1
            imagenes = os.listdir(ruta_carpeta)
            imagenes = [img for img in imagenes if img.endswith(".png") and img != "zgrafico_puntaje.png"]

            for imagen in sorted(imagenes):
                ruta_imagen = os.path.join(ruta_carpeta, imagen)
                if not os.path.exists(ruta_imagen):
                    continue
                if i % 2 == 0:
                    a = 960
                else:
                    a = 180
                    b += 240
                otra_imagen = Image.open(ruta_imagen)
                imagen_redimensionada = otra_imagen.resize((700, 200))
                plantilla.paste(imagen_redimensionada, (a, b))
                i += 1

            if os.path.exists(ruta_grafico_puntaje):
                grafico_puntaje_img = Image.open(ruta_grafico_puntaje).resize((900, 200))
                plantilla.paste(grafico_puntaje_img, (300, 260))

            os.makedirs(ruta_guardar, exist_ok=True)
            resultado_path = os.path.join(ruta_guardar, f"{estudiante.usuario}_reporte_simulacro.png")
            plantilla.save(resultado_path)

        messages.success(request, "Gráficos y reportes generados exitosamente para todos los estudiantes.")
        return redirect('seleccionar_fecha_generacion')

    except Exception as e:
        print(f"Error al generar todo el reporte: {e}")
        raise Http404("Ocurrió un error al generar los reportes.")



@login_required
@estudiante_tipo_requerido(['administrador'])
def generar_todo_reporte_respaldo(request):
    try:
        estudiantes = Estudiante.objects.all()

        ruta_guardar = 'media/reportes/simulacros'
        plantilla_path = "D:/RobertHooke/login/static/img/plantilla-notas.png"
        if not os.path.exists(plantilla_path):
            raise Http404("No se encontró la plantilla del reporte.")

        for estudiante in estudiantes:
            reportes = estudiante.reportes.all().order_by('fecha_de_examen')
            if not reportes.exists():
                continue

            # --------------------------------------
            # 1. Generar gráficos por curso
            # --------------------------------------
            cursos_data = {}
            for reporte in reportes:
                fecha = reporte.fecha_de_examen
                datos_cursos = reporte.obtener_datos()

                for curso, (corr, inc) in datos_cursos.items():
                    if curso not in cursos_data:
                        cursos_data[curso] = []
                    cursos_data[curso].append({
                        'Fecha Simulacro': fecha,
                        'correctas': corr,
                        'incorrectas': inc,
                    })

            for curso, datos in cursos_data.items():
                crear_grafico_estudiante_curso(estudiante, curso, datos)

            # --------------------------------------
            # 2. Generar gráfico de línea: Puntaje
            # --------------------------------------
            fechas = [r.fecha_de_examen.strftime('%Y-%m-%d') for r in reportes]
            puntajes = [r.obtener_total_puntaje() for r in reportes]

            ###############################

            def generar_grafico_puntaje_barras(x, y):
                fig, ax = plt.subplots(figsize=(6, 3))

                # Color solicitado
                color_barras = '#DA880B'

                # Crear gráfico de barras
                barras = ax.bar(x, y, color=color_barras)
                for spine in ax.spines.values():
                    spine.set_visible(False)

                # Quitar títulos y etiquetas de ejes
                ax.set_title("")
                ax.set_xlabel("")
                ax.set_ylabel("")

                # Mostrar etiquetas de puntaje encima de cada barra
                for barra, valor in zip(barras, y):
                    altura = barra.get_height()
                    ax.text(barra.get_x() + barra.get_width() / 2, altura + 1, f'{valor}', 
                            ha='center', va='bottom', fontsize=20, fontweight='bold')

                # Fechas en eje X
                tamaño_letra = 10 if len(x) > 5 else 10
                plt.xticks(rotation=0, fontsize=tamaño_letra)

                # Quitar eje Y si no quieres marcas
                ax.tick_params(axis='y', left=False, labelleft=False)
                ax.grid(False)

                # Guardar imagen
                ruta_carpeta = f'media/{estudiante.usuario}_2025/imagenes_reporte/'
                os.makedirs(ruta_carpeta, exist_ok=True)
                ruta_grafico = os.path.join(ruta_carpeta, "grafico_puntaje.png")
                fig.tight_layout()
                fig.savefig(ruta_grafico, bbox_inches='tight')
                plt.close(fig)

                return ruta_grafico
            

            ########################################33

            ruta_grafico_puntaje = generar_grafico_puntaje_barras(fechas, puntajes)

            # --------------------------------------
            # 3. Crear imagen final con todos los gráficos
            # --------------------------------------
            plantilla = Image.open(plantilla_path)
            draw = ImageDraw.Draw(plantilla)
            fuente = ImageFont.truetype("arial.ttf", 40)
            draw.text((720, 124), estudiante.nombre, fill="black", font=fuente)

            a, b, i = 180, 210, 1
            imagenes = [
                "Aritmética.png", "Biología.png", "Economía.png", "Filosofía.png",
                "Física.png", "Geografía.png", "Geometría.png", "Historia.png",
                "Lenguaje.png", "Literatura.png", "Psicología.png", "Química.png",
                "Razonamiento_Matemático.png", "Razonamiento_Verbal.png", "Álgebra.png",
                "Trigonometría.png",
            ]

            ruta_carpeta = f'media/{estudiante.usuario}_2025/imagenes_reporte/'

            for imagen in imagenes:
                ruta_imagen = os.path.join(ruta_carpeta, imagen)
                if not os.path.exists(ruta_imagen):
                    continue
                if i % 2 == 0:
                    a = 960
                else:
                    a = 180
                    b += 240
                otra_imagen = Image.open(ruta_imagen)
                imagen_redimensionada = otra_imagen.resize((700, 200))
                plantilla.paste(imagen_redimensionada, (a, b))
                i += 1

            #Agregar gráfico de puntajes  
            if os.path.exists(ruta_grafico_puntaje):
                grafico_puntaje_img = Image.open(ruta_grafico_puntaje).resize((900, 200))
                plantilla.paste(grafico_puntaje_img, (300, 260))

            os.makedirs(ruta_guardar, exist_ok=True)
            resultado_path = os.path.join(ruta_guardar, f"{estudiante.usuario}_reporte_simulacro.png")
            plantilla.save(resultado_path)

        messages.success(request, "Gráficos y reportes generados exitosamente para todos los estudiantes.")
        return redirect('seleccionar_fecha_generacion')

    except Exception as e:
        print(f"Error al generar todo el reporte: {e}")
        raise Http404("Ocurrió un error al generar los reportes.")


def crear_grafico_estudiante_curso(estudiante, nombre_curso, datos):
    if not datos:
        return

    df = pd.DataFrame(datos)
    if df.empty:
        return

    df['Fecha Simulacro'] = pd.to_datetime(df['Fecha Simulacro'])
    df = df.sort_values('Fecha Simulacro')

    df['blanco'] = df['total'] - df['correctas'] - df['incorrectas']

    fechas = df['Fecha Simulacro'].unique()
    cols = 3
    rows = math.ceil(len(fechas) / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(20, 5 * rows))
    axes = axes.flatten()

    for i, fecha in enumerate(fechas):
        datos_fecha = df[df['Fecha Simulacro'] == fecha]
        ax = axes[i]

        index = range(len(datos_fecha))
        bar_width = 0.2

        bars1 = ax.bar(index, datos_fecha['correctas'] * 0.85, bar_width, color='green')
        bars2 = ax.bar([i + bar_width for i in index], datos_fecha['incorrectas'] * 0.85, bar_width, color='red')
        bars3 = ax.bar([i + 2 * bar_width for i in index], datos_fecha['blanco'] * 0.85, bar_width, color='gray')

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.set_xticks([])
        ax.set_xlabel(fecha.strftime('%d/%m/%Y'), fontsize=30)
        ax.set_yticks([])

        for bars, original_values in zip([bars1, bars2, bars3], [datos_fecha['correctas'], datos_fecha['incorrectas'], datos_fecha['blanco']]):
            for bar, original_value in zip(bars, original_values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, height + 0.03, f"{int(original_value)}", ha='center', fontsize=40, fontweight='bold')

    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.subplots_adjust(bottom=0.15)

    carpeta = f'media/{estudiante.usuario}_2025/imagenes_reporte/'
    os.makedirs(carpeta, exist_ok=True)
    img_path = os.path.join(carpeta, f"{nombre_curso.replace(' ', '_')}.png")
    plt.savefig(img_path, dpi=300)
    plt.close()






def crear_grafico_estudiante_curso_respaldo(estudiante, nombre_curso, datos):
    df = pd.DataFrame(datos)
    if df.empty:
        return

    df['Fecha Simulacro'] = pd.to_datetime(df['Fecha Simulacro'])
    df = df.sort_values('Fecha Simulacro')
    df['blanco'] = 10 - df['correctas'] - df['incorrectas']

    fechas = df['Fecha Simulacro'].unique()
    cols = 3
    rows = math.ceil(len(fechas) / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(20, 5 * rows))
    axes = axes.flatten()

    for i, fecha in enumerate(fechas):
        datos_fecha = df[df['Fecha Simulacro'] == fecha]
        ax = axes[i]

        index = range(len(datos_fecha))
        bar_width = 0.2

        bars1 = ax.bar(index, datos_fecha['correctas'] * 0.85, bar_width, color='green')
        bars2 = ax.bar([i + bar_width for i in index], datos_fecha['incorrectas'] * 0.85, bar_width, color='red')
        bars3 = ax.bar([i + 2 * bar_width for i in index], datos_fecha['blanco'] * 0.85, bar_width, color='gray')

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.set_xticks([])
        ax.set_xlabel(fecha.strftime('%d/%m/%Y'), fontsize=30)
        ax.set_yticks([])

        for bars, original_values in zip([bars1, bars2, bars3], [datos_fecha['correctas'], datos_fecha['incorrectas'], datos_fecha['blanco']]):
            for bar, original_value in zip(bars, original_values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, height + 0.03, f"{int(original_value)}", ha='center', fontsize=40, fontweight='bold')

    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.subplots_adjust(bottom=0.15)

    carpeta = f'media/{estudiante.usuario}_2025/imagenes_reporte/'
    os.makedirs(carpeta, exist_ok=True)
    img_path = os.path.join(carpeta, f"{nombre_curso.replace(' ', '_')}.png")
    plt.savefig(img_path, dpi=300)
    plt.close()

@login_required
@estudiante_tipo_requerido(['administrador'])
def generar_graficos_todos_estudiantes(request):
    estudiantes = Estudiante.objects.all()

    for estudiante in estudiantes:
        reportes = estudiante.reportes.all().order_by('fecha_de_examen')
        if not reportes.exists():
            continue

        # Diccionario con listas de dicts por curso
        cursos_data = {}

        for reporte in reportes:
            fecha = reporte.fecha_de_examen
            datos_cursos = reporte.obtener_datos()  # ✅ Aquí obtenemos (correctas, incorrectas)

            for curso, (corr, inc) in datos_cursos.items():
                if curso not in cursos_data:
                    cursos_data[curso] = []

                cursos_data[curso].append({
                    'Fecha Simulacro': fecha,
                    'correctas': corr,
                    'incorrectas': inc,
                })

        # Crear un gráfico por curso
        for curso, datos in cursos_data.items():
            crear_grafico_estudiante_curso(estudiante, curso, datos)

    messages.success(request, "Gráficos generados exitosamente para todos los estudiantes.")
    return redirect('seleccionar_fecha_generacion')

@login_required
@estudiante_tipo_requerido(['administrador'])
def seleccionar_fecha_generacion(request):
    fechas_disponibles = Reporte.objects.values_list('fecha_de_examen', flat=True).distinct().order_by('-fecha_de_examen')

    if request.method == "POST":
        fecha_str = request.POST.get("fecha")
        return redirect('generar_imagenes_fecha', fecha=fecha_str)

    return render(request, 'seleccionar_fecha_reporte.html', {
        'fechas': fechas_disponibles,
        "base_template": "layouts/base.html"
    })

@login_required
@estudiante_tipo_requerido(['administrador'])
def generar_imagenes_reportes_por_fecha(request, fecha):
    fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
    cursos = [
        "Razonamiento Verbal", "Razonamiento Matemático", "Aritmética", "Álgebra",
        "Geometría", "Trigonometría", "Física", "Química", "Biología", "Lenguaje",
        "Literatura", "Historia", "Geografía", "Filosofía", "Psicología", "Economía"
    ]

    ruta_base = 'media'

    for estudiante in Estudiante.objects.all():
        reportes = Reporte.objects.filter(KK_usuario=estudiante, fecha_de_examen=fecha_obj)

        for reporte in reportes:
            datos = reporte.obtener_datos()
            carpeta_usuario = os.path.join(ruta_base, f"{estudiante.usuario}_2025")
            os.makedirs(carpeta_usuario, exist_ok=True)

            for curso, valores in datos.items():
                fig, ax = plt.subplots(figsize=(8, 4))
                correctas, incorrectas = valores
                en_blanco = 10 - (correctas + incorrectas)

                ax.bar(["Correctas", "Incorrectas", "En blanco"],
                       [correctas, incorrectas, en_blanco],
                       color=["green", "red", "gray"])
                ax.set_title(f"{curso} - {reporte.fecha_de_examen}")

                nombre_archivo = f"{curso}_{estudiante.usuario}_{reporte.fecha_de_examen}.png".replace(" ", "_")
                ruta_archivo = os.path.join(carpeta_usuario, nombre_archivo)

                plt.savefig(ruta_archivo, format='png')
                plt.close(fig)

    return redirect('seleccionar_fecha_generacion')  # Vuelve a la vista de selección con éxito

@login_required
def generar_reporte(request):
    usuario_actual = request.user
    try:
        estudiantes = Estudiante.objects.all()
        ruta_guardar = f'media/reportes/simulacros'
        plantilla_path = os.path.join(settings.MEDIA_ROOT, "D:/RobertHooke/login/static/img/plantilla-notas.png")

        for estudiante in estudiantes:
            ruta_carpeta = f'media/{estudiante.usuario}_2025/imagenes_reporte/'
            imagenes = [
                "Aritmética.png", "Biología.png", "Economía.png", "Filosofía.png",
                "Física.png", "Geografía.png", "Geometría.png", "Historia.png",
                "Lenguaje.png", "Literatura.png", "Psicología.png", "Química.png",
                "Razonamiento_Matemático.png", "Razonamiento_Verbal.png", "Álgebra.png",
                "Trigonometría.png",
            ]

            # Cargar la plantilla
            # Asegúrate de que esta plantilla exista
            plantilla = Image.open(plantilla_path)

            # Crear un objeto de dibujo
            draw = ImageDraw.Draw(plantilla)
            fuente = ImageFont.truetype("arial.ttf", 40)
            draw.text((720, 124), estudiante.nombre, fill="black", font=fuente)

            # Añadir imágenes
            a = 180
            b = 210
            i = 1
            for imagen in imagenes:
                ruta_imagen = os.path.join(ruta_carpeta, imagen)
                if not os.path.exists(ruta_imagen):
                    continue
                if i % 2 == 0:
                    a = 960
                else:
                    a = 180
                    b += 240
                otra_imagen = Image.open(ruta_imagen)
                imagen_redimensionada = otra_imagen.resize((700, 200))
                plantilla.paste(imagen_redimensionada, (a, b))
                i += 1

            resultado_path = os.path.join(ruta_guardar, f"{estudiante.usuario}_reporte_simulacro.png")
            plantilla.save(resultado_path)

            # 🔽 Aquí está el cambio importante
        messages.success(request, "Reportes generados exitosamente para todos los estudiantes.")
        return redirect("seleccionar_fecha_generacion")

    except Exception as e:
        print(f"Error al generar el reporte: {e}")
        raise Http404("No se pudo generar el reporte")

@login_required
@estudiante_tipo_requerido(['administrador'])
def generar_reportes_simulacro_todos(request):
    try:
        estudiantes = Estudiante.objects.all()
        plantilla_path = os.path.join(settings.BASE_DIR, "static/img/plantilla-notas.png")
        fuente_path = os.path.join(settings.BASE_DIR, "static/fonts/arial.ttf")  # Asegúrate que exista

        for estudiante in estudiantes:
            ruta_carpeta = f'media/{estudiante.usuario}_2025/imagenes_reporte/'
            imagenes = [
                "Aritmética.png", "Biología.png", "Economía.png", "Filosofía.png",
                "Física.png", "Geografía.png", "Geometría.png", "Historia.png",
                "Lenguaje.png", "Literatura.png", "Psicología.png", "Química.png",
                "Razonamiento_Matemático.png", "Razonamiento_Verbal.png", "Álgebra.png",
                "Trigonometría.png",
            ]

            if not os.path.exists(plantilla_path):
                continue

            plantilla = Image.open(plantilla_path)
            draw = ImageDraw.Draw(plantilla)

            try:
                fuente = ImageFont.truetype(fuente_path, 40)
            except:
                fuente = ImageFont.load_default()

            draw.text((720, 124), estudiante.nombre, fill="black", font=fuente)

            a = 180
            b = 210
            i = 1

            for imagen in imagenes:
                ruta_imagen = os.path.join(ruta_carpeta, imagen)
                if not os.path.exists(ruta_imagen):
                    continue

                if i % 2 == 0:
                    a = 960
                else:
                    a = 180
                    b += 240

                otra_imagen = Image.open(ruta_imagen)
                imagen_redimensionada = otra_imagen.resize((700, 200))
                plantilla.paste(imagen_redimensionada, (a, b))
                i += 1

            # Guardar en carpeta final
            carpeta_destino = f'media/reportes/simulacros/'
            os.makedirs(carpeta_destino, exist_ok=True)
            resultado_path = os.path.join(carpeta_destino, f"{estudiante.usuario}_reporte_simulacro.png")
            plantilla.save(resultado_path)

        messages.success(request, "Reportes generados exitosamente para todos los estudiantes.")
        return redirect("seleccionar_fecha_generacion")

    except Exception as e:
        print(f"Error al generar reportes: {e}")
        raise Http404("Error al generar los reportes.")

@login_required
@estudiante_tipo_requerido(['administrador'])
def generar_imagenes_reportes(request):
    usuario_actual = request.user
    base_template = "layouts/base.html" if usuario_actual.tipo_estudiante == "administrador" else "layouts/base2.html"

    cursos_pre = [
        "Razonamiento Verbal", "Razonamiento Matemático", "Aritmética", "Álgebra",
        "Geometría", "Trigonometría", "Física", "Química", "Biología", "Lenguaje",
        "Literatura", "Historia", "Geografía", "Filosofía", "Psicología", "Economía"
    ]

    cursos_semillero = [
        "Razonamiento Verbal", "Razonamiento Matemático", "Aritmética", "Álgebra", "Literatura"
    ]

    preguntas_por_curso_pre = {
        "Razonamiento Verbal": 15,
        "Razonamiento Matemático": 15,
        "Aritmética": 5,
        "Álgebra": 5,
        "Geometría": 4,
        "Trigonometría": 4,
        "Física": 5,
        "Química": 5,
        "Biología": 9,
        "Lenguaje": 6,
        "Literatura": 6,
        "Historia": 3,
        "Geografía": 2,
        "Filosofía": 2,
        "Psicología": 2,
        "Economía": 2,
    }

    preguntas_por_curso_semillero = {
        "Razonamiento Verbal": 10,
        "Razonamiento Matemático": 10,
        "Aritmética": 5,
        "Álgebra": 5,
        "Literatura": 5,
        "Geometría": 0,
        "Trigonometría": 0,
        "Física": 0,
        "Química": 0,
        "Biología": 0,
        "Lenguaje": 0,
        "Historia": 0,
        "Geografía": 0,
        "Filosofía": 0,
        "Psicología": 0,
        "Economía": 0,
    }

    ruta_base = r'media'
    graficos = []
    fechas = set()

    for estudiante in Estudiante.objects.all():
        reportes = Reporte.objects.filter(KK_usuario=estudiante).order_by('-fecha_de_examen')

        for reporte in reportes:
            nivel = reporte.nivel
            if nivel == "90":
                cursos = cursos_pre
                preguntas_por_curso = preguntas_por_curso_pre
            else:
                cursos = cursos_semillero
                preguntas_por_curso = preguntas_por_curso_semillero
                

            datos = reporte.obtener_datos()
            carpeta_usuario = os.path.join(ruta_base, f"{estudiante.usuario}_2025", "imagenes_reporte")
            os.makedirs(carpeta_usuario, exist_ok=True)

            for curso in cursos:
                if curso not in datos:
                    continue  # Si no hay datos para ese curso, lo omitimos
                correctas, incorrectas = datos[curso]
                total_preguntas = preguntas_por_curso.get(curso, 10)
                en_blanco = total_preguntas - (correctas + incorrectas)

                fig, ax = plt.subplots(figsize=(8, 4))
                ax.bar(["Correctas", "Incorrectas", "En blanco"],
                       [correctas, incorrectas, en_blanco],
                       color=["green", "red", "gray"])
                ax.set_title(f"{curso} - {reporte.fecha_de_examen}")

                nombre_archivo = f"{curso}_{estudiante.usuario}_{reporte.fecha_de_examen}.png".replace(" ", "_")
                ruta_archivo = os.path.join(carpeta_usuario, nombre_archivo)

                plt.savefig(ruta_archivo, format='png')

                buffer = BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                buffer.close()
                plt.close(fig)

                graficos.append({
                    "fecha": reporte.fecha_de_examen,
                    "curso": curso,
                    "grafico": image_base64
                })

            fechas.add(reporte.fecha_de_examen)

    return render(request, 'ultimo_simulacro.html', {
        'graficos': graficos,
        'fechas': sorted(fechas),
        "base_template": base_template
    })




@login_required
@estudiante_tipo_requerido(['administrador'])
def generar_imagenes_reportes_respaldo(request):
    usuario_actual = request.user
    base_template = "layouts/base.html" if usuario_actual.tipo_estudiante == "administrador" else "layouts/base2.html"

    cursos = [
        "Razonamiento Verbal", "Razonamiento Matemático", "Aritmética", "Álgebra",
        "Geometría", "Trigonometría", "Física", "Química", "Biología", "Lenguaje",
        "Literatura", "Historia", "Geografía", "Filosofía", "Psicología", "Economía"
    ]

    # Cantidad real de preguntas por curso
    preguntas_por_curso = {
        "Razonamiento Verbal": 15,
        "Razonamiento Matemático": 15,
        "Aritmética": 5,
        "Álgebra": 5,
        "Geometría": 4,
        "Trigonometría": 4,
        "Física": 5,
        "Química": 5,
        "Biología": 9,
        "Lenguaje": 6,
        "Literatura": 6,
        "Historia": 3,
        "Geografía": 2,
        "Filosofía": 2,
        "Psicología": 2,
        "Economía": 2,
    }

    ruta_base = r'media'
    graficos = []
    fechas = set()

    for estudiante in Estudiante.objects.all():
        reportes = Reporte.objects.filter(KK_usuario=estudiante).order_by('-fecha_de_examen')

        for reporte in reportes:
            datos = reporte.obtener_datos()
            carpeta_usuario = os.path.join(ruta_base, f"{estudiante.usuario}_2025")
            os.makedirs(carpeta_usuario, exist_ok=True)

            for curso, valores in datos.items():
                correctas, incorrectas = valores
                total_preguntas = preguntas_por_curso.get(curso, 10)  # Si no se encuentra, usa 10 como fallback
                en_blanco = total_preguntas - (correctas + incorrectas)

                fig, ax = plt.subplots(figsize=(8, 4))
                ax.bar(["Correctas", "Incorrectas", "En blanco"],
                       [correctas, incorrectas, en_blanco],
                       color=["green", "red", "gray"])

                ax.set_title(f"{curso} - {reporte.fecha_de_examen}")

                nombre_archivo = f"{curso}_{estudiante.usuario}_{reporte.fecha_de_examen}.png".replace(" ", "_")
                ruta_archivo = os.path.join(carpeta_usuario, nombre_archivo)

                plt.savefig(ruta_archivo, format='png')

                buffer = BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                buffer.close()
                plt.close(fig)

                graficos.append({
                    "fecha": reporte.fecha_de_examen,
                    "curso": curso,
                    "grafico": image_base64
                })

            fechas.add(reporte.fecha_de_examen)

    return render(request, 'ultimo_simulacro.html', {
        'graficos': graficos,
        'cursos': cursos,
        'fechas': sorted(fechas),
        "base_template": base_template
    })




@login_required
def reportes_estudiante(request):
    usuario_actual = request.user

    base_template = "layouts/base.html" if usuario_actual.tipo_estudiante == "administrador" else "layouts/base2.html"

    reportes = Reporte.objects.filter(KK_usuario=usuario_actual).order_by('-fecha_de_examen')

    cursos = [
        "Razonamiento Verbal", "Razonamiento Matemático", "Aritmética", "Álgebra",
        "Geometría", "Trigonometría", "Física", "Química", "Biología", "Lenguaje",
        "Literatura", "Historia", "Geografía", "Filosofía", "Psicología", "Economía"
    ]

    fechas = list(reportes.values_list('fecha_de_examen', flat=True).distinct())
    graficos = []

    # Ruta base dentro de MEDIA_ROOT
    carpeta_usuario = os.path.join(settings.MEDIA_ROOT, f"{usuario_actual.usuario}_2025")

    for reporte in reportes:
        datos = reporte.obtener_datos()

        for curso in datos.keys():
            # Generar el nombre del archivo según la estructura "curso_usuario_fecha.png"
            nombre_archivo = f"{curso}_{usuario_actual.usuario}_{reporte.fecha_de_examen}.png".replace(" ", "_")
            ruta_relativa = os.path.join(f"{usuario_actual.usuario}_2025", nombre_archivo)
            ruta_absoluta = os.path.join(settings.MEDIA_ROOT, ruta_relativa)

            # Verificar si el archivo realmente existe antes de agregarlo
            if os.path.exists(ruta_absoluta):
                graficos.append({
                    "fecha": reporte.fecha_de_examen,
                    "curso": curso,
                    "ruta_imagen": f"{settings.MEDIA_URL}{ruta_relativa.replace('\\', '/')}"
                })
    
    return render(request, 'home.html', {
        'graficos': graficos,
        'cursos': cursos,
        'fechas': fechas,
        "base_template": base_template
    })

@login_required
def reportes_observaciones(request):
    usuario_actual = request.user
    if usuario_actual.tipo_estudiante == "administrador":  
        base_template = "layouts/base.html"  # Plantilla para administrador
    else:
        base_template = "layouts/base2.html"  # Plantilla para estudiante regular

    reportes = Reporte.objects.filter(KK_usuario=usuario_actual).order_by('-fecha_de_examen')

    observaciones = [
        {"fecha": reporte.fecha_de_examen.strftime('%Y-%m-%d'), "texto": reporte.Observacion}
        for reporte in reportes
    ]

    return render(request, 'observaciones.html', {'observaciones': observaciones, "base_template": base_template})

@login_required
def reportes_puesto_puntaje(request):
    usuario_actual = request.user
    if usuario_actual.tipo_estudiante == "administrador":  
        base_template = "layouts/base.html"
    else:
        base_template = "layouts/base2.html"

    reportes = Reporte.objects.filter(KK_usuario=usuario_actual).order_by('fecha_de_examen')

    fechas = [reporte.fecha_de_examen.strftime('%Y-%m-%d') for reporte in reportes]
    puestos = [reporte.puesto for reporte in reportes]
    puntajes = [reporte.obtener_total_puntaje() for reporte in reportes]

    def generar_grafico(x, y, titulo, xlabel, ylabel, color, invertir_y = False):
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(x, y, marker='o', linestyle='-', color=color)
        ax.set_title(titulo)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True)

        if invertir_y:
            ax.invert_yaxis()

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        imagen_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        plt.close(fig)

        return imagen_base64

    grafico_puesto = generar_grafico(fechas, puestos, "Evolución del Puesto", "Fecha", "Puesto", "blue", invertir_y=True)
    grafico_puntaje = generar_grafico(fechas, puntajes, "Evolución del Puntaje", "Fecha", "Puntaje", "green")

    # Obtener nombre y último puntaje
    nombre_usuario = usuario_actual.nombre or usuario_actual.username
    ultimo_puntaje = puntajes[-1] if puntajes else None

    return render(request, 'ultimo_simulacro.html', {
        'grafico_puesto': grafico_puesto,
        'grafico_puntaje': grafico_puntaje,
        'base_template': base_template,
        'nombre_usuario': nombre_usuario,
        'ultimo_puntaje': ultimo_puntaje,
    })


#Administración de estudiantes
@require_POST
@login_required
@estudiante_tipo_requerido(['administrador'])
def eliminar_estudiantes_masivo(request):
    ids = request.POST.getlist('estudiantes')
    ids = [id for id in ids if id.isdigit()]
    
    if ids:
        estudiantes = Estudiante.objects.filter(ID_Estudiante__in=ids)
        
        for estudiante in estudiantes:
            # Ruta a la carpeta del estudiante
            carpeta_estudiante = os.path.join('media', f"{estudiante.usuario}_2025")

            # Eliminar carpeta si existe
            if os.path.exists(carpeta_estudiante) and os.path.isdir(carpeta_estudiante):
                shutil.rmtree(carpeta_estudiante)

        # Eliminar los estudiantes después de borrar las carpetas
        estudiantes.delete()
        
        messages.success(request, "Estudiantes y carpetas eliminados correctamente.")
    else:
        messages.warning(request, "No seleccionaste ningún estudiante válido.")
    
    return redirect('lista_estudiantes')

@login_required
@estudiante_tipo_requerido(['administrador'])
def agregar_observacion(request, estudiante_id):
    usuario_actual = request.user

    # Definir la plantilla según el tipo de usuario
    base_template = "layouts/base.html" if usuario_actual.tipo_estudiante == "administrador" else "layouts/base2.html"
    estudiante = get_object_or_404(Estudiante, ID_Estudiante=estudiante_id)
    reportes = Reporte.objects.filter(KK_usuario=estudiante)
    
    fecha_str = request.GET.get('fecha')
    fecha_obj = None

    if fecha_str:
        try:
            # Forzar que la fecha esté en formato YYYY-MM-DD
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            return HttpResponseBadRequest("Formato de fecha inválido")

    if request.method == 'POST':
        observacion = request.POST.get('observacion')
        if not fecha_obj:
            return HttpResponseBadRequest("Falta la fecha del examen")

        reporte = reportes.filter(fecha_de_examen=fecha_obj).first()
        if reporte:
            reporte.Observacion = observacion
            reporte.save()
            return redirect('lista_estudiantes')  # o a donde quieras redirigir
        else:
            return HttpResponseBadRequest("No se encontró el reporte para esa fecha")

    return render(request, 'agregar_observacion.html', {
        'estudiante': estudiante,
        'reportes': reportes,
        'base_template': base_template,
        'fecha_seleccionada': fecha_obj,
        'reporte_seleccionado': reportes.filter(fecha_de_examen=fecha_obj).first() if fecha_obj else None
    })

@login_required
@estudiante_tipo_requerido(['administrador'])
def lista_estudiantes(request):
    usuario_actual = request.user

    # Definir la plantilla según el tipo de usuario
    base_template = "layouts/base.html" if usuario_actual.tipo_estudiante == "administrador" else "layouts/base2.html"
    query = request.GET.get('q', '')
    if query:
        estudiantes = Estudiante.objects.filter(nombre__icontains=query)
    else:
        estudiantes = Estudiante.objects.filter(tipo_estudiante = "estudiante")
    return render(request, 'lista_estudiantes.html', {
        'estudiantes': estudiantes,
        'query': query, 
        "base_template": base_template
    })

@login_required
@estudiante_tipo_requerido(['administrador'])
def editar_estudiante(request, pk):
    usuario_actual = request.user

    # Definir la plantilla según el tipo de usuario
    base_template = "layouts/base.html" if usuario_actual.tipo_estudiante == "administrador" else "layouts/base2.html"
    estudiante = get_object_or_404(Estudiante, pk=pk)
    if request.method == 'POST':
        form = EstudianteForm2(request.POST, instance=estudiante)
        if form.is_valid():
            form.save()
            return redirect('lista_estudiantes')
    else:
        form = EstudianteForm2(instance=estudiante)
    return render(request, 'editar_estudiante.html', {'form': form, "base_template": base_template})

@login_required
@estudiante_tipo_requerido(['administrador'])
def eliminar_estudiante(request, pk):
    usuario_actual = request.user
    base_template = "layouts/base.html" if usuario_actual.tipo_estudiante == "administrador" else "layouts/base2.html"

    estudiante = get_object_or_404(Estudiante, pk=pk)

    if request.method == 'POST':
        # Ruta base donde están las carpetas de los estudiantes
        ruta_base = r'media'

        # Nombre de la carpeta del estudiante: "usuario2025"
        carpeta_estudiante = os.path.join(ruta_base, f"{estudiante.usuario}_2025")

        # Verifica si la carpeta existe y elimínala
        if os.path.exists(carpeta_estudiante) and os.path.isdir(carpeta_estudiante):
            shutil.rmtree(carpeta_estudiante)  # Elimina la carpeta completa y su contenido

        # Luego elimina el estudiante de la base de datos
        estudiante.delete()
        return redirect('lista_estudiantes')

    return render(request, 'eliminar_estudiante.html', {'estudiante': estudiante, "base_template": base_template})


@login_required
@estudiante_tipo_requerido(['administrador'])
def cargar_asistencias(request):
    estudiante = request.user
    if estudiante.tipo_estudiante == "administrador":  
        base_template = "layouts/base.html"  # Plantilla para administrador
    else:
        base_template = "layouts/base2.html"  # Plantilla para estudiante regular
    if request.method == 'POST':
        form = CargarExcelForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_excel = request.FILES['archivo_excel']
            try:
                df = pd.read_excel(archivo_excel)
                columnas_esperadas = [
                    'Cód. Alumno', 'Fecha', 'Marca 01', 'Marca 02', 'Marca 03', 'Marca 04', 'Marca 05', 'Marca 06', 'Observ'
                ]
                if not all(col in df.columns for col in columnas_esperadas):
                    messages.error(request, "El archivo Excel no tiene las columnas esperadas.")
                    return redirect('subir_asistencia')
                for _, fila in df.iterrows():
                    estudiante = Estudiante.objects.get(usuario=fila['Cód. Alumno'])
                    Asistencia.objects.create(
                        KK_usuario=estudiante,
                        Fecha=fila['Fecha'],
                        Ingreso_mana=fila['Marca 01'],
                        Salida_mana=fila['Marca 02'],
                        Ingreso_tarde=fila['Marca 03'],
                        Salida_tarde=fila['Marca 04'],
                        Ingreso_noche=fila['Marca 05'],
                        Salida_noche=fila['Marca 06'],
                        Observacion=fila['Observ']
                    )
                messages.success(request, "Datos cargados exitosamente.")
                return redirect('subir_asistencia')

            except Estudiante.DoesNotExist:
                messages.error(request, "El usuario no existe en la base de datos.")
                return redirect('subir_asistencia')
            except Exception as e:
                messages.error(request, f"Error al procesar el archivo: {str(e)}")
                return redirect('subir_asistencia')
    else:
        form = CargarExcelForm()
    
    return render(request, "subir_asistencia.html", {"base_template": base_template, "form": form})


@login_required
@estudiante_tipo_requerido(['administrador'])
def subir_reporte(request):
    estudiante = request.user
    base_template = "layouts/base.html" if estudiante.tipo_estudiante == "administrador" else "layouts/base2.html"

    if request.method == 'POST':
        form = CargarExcelFormReporte(request.POST, request.FILES)
        if form.is_valid():
            archivo_excel = request.FILES['archivo_excel']
            nivel = int(form.cleaned_data['nivel'])  # 30 o 90

            try:
                df = pd.read_excel(archivo_excel)

                columnas_semi = ['Alumno', 'Fecha Simulacro', 'Puesto', 'Rv_1', 'Rv_2', 'Rm_1', 'Rm_2', 'Ar_1', 'Ar_2', 'Al_1', 'Al_2', 'Lit_1', 'Lit_2', 'Observacion'
                ]
                columnas_pre = [
                    'Alumno', 'Fecha Simulacro', 'Puesto', 'Rv_1', 'Rv_2', 'Rm_1', 'Rm_2', 'Ar_1', 'Ar_2', 'Al_1', 'Al_2','Ge_1', 'Ge_2', 'Tr_1', 'Tr_2', 'Fi_1', 'Fi_2', 'Qu_1', 'Qu_2', 'Bi_1', 'Bi_2','Le_1', 'Le_2', 'Lit_1', 'Lit_2', 'Hi_1', 'Hi_2', 'Gf_1', 'Gf_2', 'Fil_1', 'Fil_2','Psi_1', 'Psi_2', 'Ec_1', 'Ec_2', 'Observacion'
                ]

                # Validar columnas según nivel
                if nivel == 30 and not all(col in df.columns for col in columnas_semi):
                    messages.error(request, "El archivo no tiene las columnas esperadas para nivel Semillero, revise los campos por favor: 'Alumno', 'Fecha Simulacro', 'Puesto', 'Rv_1', 'Rv_2', 'Rm_1', 'Rm_2', 'Ar_1', 'Ar_2', 'Al_1', 'Al_2', 'Lit_1', 'Lit_2', 'Observacion'")
                    return redirect('subir_reporte')
                if nivel == 90 and not all(col in df.columns for col in columnas_pre):
                    messages.error(request, "El archivo no tiene las columnas esperadas para nivel Pre: 'Alumno', 'Fecha Simulacro', 'Puesto', 'Rv_1', 'Rv_2', 'Rm_1', 'Rm_2', 'Ar_1', 'Ar_2', 'Al_1', 'Al_2','Ge_1', 'Ge_2', 'Tr_1', 'Tr_2', 'Fi_1', 'Fi_2', 'Qu_1', 'Qu_2', 'Bi_1', 'Bi_2','Le_1', 'Le_2', 'Lit_1', 'Lit_2', 'Hi_1', 'Hi_2', 'Gf_1', 'Gf_2', 'Fil_1', 'Fil_2','Psi_1', 'Psi_2', 'Ec_1', 'Ec_2', 'Observacion'")
                    return redirect('subir_reporte')

                for _, fila in df.iterrows():
                    try:
                        estudiante = Estudiante.objects.get(usuario=fila['Alumno'])

                        # Campos comunes
                        datos = {
                            "KK_usuario": estudiante,
                            "fecha_de_examen": fila.get('Fecha Simulacro'),
                            "puesto": fila.get('Puesto'),
                            "nivel": nivel,
                            "Observacion": fila.get('Observacion'),
                            "Rv_1": fila.get("Rv_1", 0),
                            "Rv_2": fila.get("Rv_2", 0),
                            "Rm_1": fila.get("Rm_1", 0),
                            "Rm_2": fila.get("Rm_2", 0),
                            "Ar_1": fila.get("Ar_1", 0),
                            "Ar_2": fila.get("Ar_2", 0),
                            "Al_1": fila.get("Al_1", 0),
                            "Al_2": fila.get("Al_2", 0),
                            "Lit_1": fila.get("Lit_1", 0),
                            "Lit_2": fila.get("Lit_2", 0),
                        }

                        # Si es Pre (90), añadimos todas las demás
                        if nivel == 90:
                            datos.update({
                                "Ge_1": fila.get("Ge_1", 0), "Ge_2": fila.get("Ge_2", 0),
                                "Tr_1": fila.get("Tr_1", 0), "Tr_2": fila.get("Tr_2", 0),
                                "Fi_1": fila.get("Fi_1", 0), "Fi_2": fila.get("Fi_2", 0),
                                "Qu_1": fila.get("Qu_1", 0), "Qu_2": fila.get("Qu_2", 0),
                                "Bi_1": fila.get("Bi_1", 0), "Bi_2": fila.get("Bi_2", 0),
                                "Le_1": fila.get("Le_1", 0), "Le_2": fila.get("Le_2", 0),
                                "Hi_1": fila.get("Hi_1", 0), "Hi_2": fila.get("Hi_2", 0),
                                "Gf_1": fila.get("Gf_1", 0), "Gf_2": fila.get("Gf_2", 0),
                                "Fil_1": fila.get("Fil_1", 0), "Fil_2": fila.get("Fil_2", 0),
                                "Psi_1": fila.get("Psi_1", 0), "Psi_2": fila.get("Psi_2", 0),
                                "Ec_1": fila.get("Ec_1", 0), "Ec_2": fila.get("Ec_2", 0),
                            })
                        else:
                            # Semillero: rellenamos todo lo demás con ceros
                            for campo in ['Ge', 'Tr', 'Fi', 'Qu', 'Bi', 'Le', 'Hi', 'Gf', 'Fil', 'Psi', 'Ec']:
                                datos[f"{campo}_1"] = 0
                                datos[f"{campo}_2"] = 0

                        Reporte.objects.create(**datos)

                    except Estudiante.DoesNotExist:
                        messages.error(request, f"El estudiante '{fila['Alumno']}' no existe.")
                        continue

                messages.success(request, "Datos cargados exitosamente.")
                return redirect('subir_reporte')

            except Exception as e:
                messages.error(request, f"Error al procesar el archivo: {str(e)}")

        else:
            messages.error(request, "Formulario inválido. Por favor, verifica los datos.")

    else:
        form = CargarExcelFormReporte()

    return render(request, "subir_reporte.html", {
        "base_template": base_template,
        "form": form
    })






@login_required
@estudiante_tipo_requerido(['administrador'])
def subir_reporte_respaldo(request):
    
    estudiante = request.user
    if estudiante.tipo_estudiante == "administrador":  
        base_template = "layouts/base.html"  # Plantilla para administrador
    else:
        base_template = "layouts/base2.html"  # Plantilla para estudiante regular

    if request.method == 'POST':
        form = CargarExcelForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_excel = request.FILES['archivo_excel']
            try:
                # Leer el archivo Excel
                df = pd.read_excel(archivo_excel)

                # Validar que el archivo tenga las columnas correctas
                columnas_esperadas = [
                    'Alumno', 'Fecha Simulacro', 'Puesto', 'Rv_1', 'Rv_2', 'Rm_1', 'Rm_2', 'Ar_1', 'Ar_2', 'Al_1', 'Al_2','Ge_1', 'Ge_2', 'Tr_1', 'Tr_2', 'Fi_1', 'Fi_2', 'Qu_1', 'Qu_2', 'Bi_1', 'Bi_2','Le_1', 'Le_2', 'Lit_1', 'Lit_2', 'Hi_1', 'Hi_2', 'Gf_1', 'Gf_2', 'Fil_1', 'Fil_2','Psi_1', 'Psi_2', 'Ec_1', 'Ec_2', 'Observación'
                ]
                if not all(col in df.columns for col in columnas_esperadas):
                    messages.error(request, "El archivo Excel no tiene las columnas esperadas.")
                    return redirect('subir_reporte')

                # Procesar cada fila del archivo Excel
                for _, fila in df.iterrows():
                    estudiante = Estudiante.objects.get(usuario=fila['Alumno'])
                    Reporte.objects.create(
                        KK_usuario=estudiante,
                        Rv_1=fila['Rv_1'],
                        Rv_2=fila['Rv_2'],
                        Rm_1=fila['Rm_1'],
                        Rm_2=fila['Rm_2'],
                        Ar_1=fila['Ar_1'],
                        Ar_2=fila['Ar_2'],
                        Al_1=fila['Al_1'],
                        Al_2=fila['Al_2'],
                        Ge_1=fila['Ge_1'],
                        Ge_2=fila['Ge_2'],
                        Tr_1=fila['Tr_1'],
                        Tr_2=fila['Tr_2'],
                        Fi_1=fila['Fi_1'],
                        Fi_2=fila['Fi_2'],
                        Qu_1=fila['Qu_1'],
                        Qu_2=fila['Qu_2'],
                        Bi_1=fila['Bi_1'],
                        Bi_2=fila['Bi_2'],
                        Le_1=fila['Le_1'],
                        Le_2=fila['Le_2'],
                        Lit_1=fila['Lit_1'],
                        Lit_2=fila['Lit_2'],
                        Hi_1=fila['Hi_1'],
                        Hi_2=fila['Hi_2'],
                        Gf_1=fila['Gf_1'],
                        Gf_2=fila['Gf_2'],
                        Fil_1=fila['Fil_1'],
                        Fil_2=fila['Fil_2'],
                        Psi_1=fila['Psi_1'],
                        Psi_2=fila['Psi_2'],
                        Ec_1=fila['Ec_1'],
                        Ec_2=fila['Ec_2'],
                        Observacion=fila['Observación'],
                        fecha_de_examen=fila['Fecha Simulacro'],
                        puesto=fila['Puesto']
                    )

                messages.success(request, "Datos cargados exitosamente.")
                return redirect('subir_reporte')

            except Estudiante.DoesNotExist:
                messages.error(request, "El IDEstudiante no existe en la base de datos.")
                return redirect('subir_reporte')
            except Exception as e:
                messages.error(request, f"Error al procesar el archivo: {str(e)}")
                return redirect('subir_reporte')
    else:
        form = CargarExcelForm()
    
    return render(request, "subir_reporte.html", {"base_template": base_template, "form": form})

@login_required
@estudiante_tipo_requerido(['administrador'])
def cargar_excel(request):
    estudiante = request.user
    if estudiante.tipo_estudiante == "administrador":  
        base_template = "layouts/base.html"  # Plantilla para administrador
    else:
        base_template = "layouts/base2.html"  # Plantilla para estudiante regular

    RUTA_BASE_ESTUDIANTES = r'media'

    if request.method == 'POST':
        form = CargarExcelForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_excel = request.FILES['archivo_excel']
            
            try:
                # Leer el archivo Excel
                df = pd.read_excel(archivo_excel)
                
                # Verificar que el archivo tenga las columnas correctas
                if not all(col in df.columns for col in ['nombre', 'usuario', 'contraseña']):
                    messages.error(request, 'El archivo Excel debe tener las columnas: nombre, usuario, contraseña.')
                    return redirect('cargar_excel')
                
                # Procesar cada fila del archivo
                for index, row in df.iterrows():
                    nombre = row['nombre']
                    usuario = row['usuario']
                    contraseña = row['contraseña']
                    
                    # Verificar si el usuario ya existe
                    if Estudiante.objects.filter(usuario=usuario).exists():
                        messages.warning(request, f'El usuario {usuario} ya existe y no fue registrado.')
                    else:
                        # Crear un nuevo estudiante
                        Estudiante.objects.create(
                            nombre=nombre,
                            usuario=usuario,
                            contraseña=contraseña
                        )
                        # Crear la carpeta del estudiante
                        carpeta_estudiante = os.path.join(RUTA_BASE_ESTUDIANTES, f"{usuario}_2025")

                        subcarpeta_imagenes = os.path.join(carpeta_estudiante, "imagenes_reporte")
                        if not os.path.exists(carpeta_estudiante):
                            os.makedirs(subcarpeta_imagenes, exist_ok=True)
        
                messages.success(request, f'Estudiante {usuario} registrado correctamente y carpeta creada.')
                
                messages.success(request, 'Archivo procesado correctamente.')
                return redirect('cargar_excel')
            
            except Exception as e:
                messages.error(request, f'Error al procesar el archivo: {str(e)}')
                return redirect('cargar_excel')
    else:
        form = CargarExcelForm()
    
    return render(request, "cargar_excel.html", {"base_template": base_template, "form": form})

@login_required
def crearAlumno(request):
    return render(request, 'crear_alumno.html')






def prueba(request):
    usuario_actual = request.user
    # Definir la plantilla según el tipo de usuario
    base_template = "layouts/base.html"
    return render(request, 'prueba.html', {
        'base_template': base_template,
    })















def logout_view(request):

    estudiante = request.user
    if estudiante.tipo_estudiante == "administrador":  
        base_template = "layouts/base.html"  # Plantilla para administrador
    else:
        base_template = "layouts/base2.html"  # Plantilla para estudiante regular
    logout(request)

    return render(request, "home.html", {"base_template": base_template})




def login_view(request):
    user = request.user
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data['usuario']
            contraseña = form.cleaned_data['contraseña']
            
            # Autenticar usando el backend personalizado
            backend = EstudianteBackend()
            estudiante = backend.authenticate(request, username=usuario, password=contraseña)
            
            if estudiante is not None:
                login(request, estudiante, backend='tu_app.backends.EstudianteBackend')
                messages.success(request, 'Inicio de sesión exitoso.')
                return redirect('nombre_de_la_vista_protegida')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    
    return render(request, 'registration/login.html', {'form': form}, {'user': user})


@login_required
@estudiante_tipo_requerido(['administrador'])
def registrar_estudiante(request):
    estudiante = request.user
    if estudiante.tipo_estudiante == "administrador":  
        base_template = "layouts/base.html"  # Plantilla para administrador
    else:
        base_template = "layouts/base2.html"  # Plantilla para estudiante regular

    if request.method == 'POST':
        form = EstudianteForm(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data['usuario']
            if Estudiante.objects.filter(usuario=usuario).exists():
                messages.error(request, 'El usuario ya existe.')
            else:
                nuevo_estudiante = form.save()

                # Definir la ruta donde se crearán las carpetas
                ruta_base = r'media'
                
                # Crear la carpeta con el formato "usuario2025"
                carpeta_estudiante = os.path.join(ruta_base, f"{usuario}_2025")

                subcarpeta_imagenes = os.path.join(carpeta_estudiante, "imagenes_reporte")

                os.makedirs(subcarpeta_imagenes, exist_ok=True)

                messages.success(request, 'Estudiante creado correctamente y carpeta asignada.')
                return redirect('registrar_estudiante')
        else:
            messages.error(request, 'Error al crear el estudiante. Revise los datos.')
    else:
        form = EstudianteForm()

    return render(request, "registrar_estudiante.html", {"base_template": base_template, "form": form})

@login_required
def base(request):
    estudiante = request.user
    if estudiante.tipo_estudiante == "administrador":  
        base_template = "layouts/base.html"  # Plantilla para administrador
    else:
        base_template = "layouts/base2.html"  # Plantilla para estudiante regular

    return render(request, "registration/login.html", {"base_template": base_template})


@login_required
def home(request):
    estudiante = request.user
    if estudiante.tipo_estudiante == "administrador":  
        base_template = "layouts/base.html"  # Plantilla para administrador
    else:
        base_template = "layouts/base2.html"  # Plantilla para estudiante regular

    return render(request, "home.html", {"base_template": base_template})

def inicio(request):
    return render(request, 'registration/login.html');


def salir(request):
    logout(request)
    return redirect('home')


def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
    return render(request, 'login.html')

@login_required
def upload_excel(request):
    estudiante = request.user
    if estudiante.tipo_estudiante == "administrador":  
        base_template = "layouts/base.html"  # Plantilla para administrador
    else:
        base_template = "layouts/base2.html"  # Plantilla para estudiante regular
    if request.method == "POST":
        excel_file = request.FILES["excel_file"]
        try:
            df = pd.read_excel(excel_file)
            for index, row in df.iterrows():
                username = row['Usuario']
                password = row['Contraseña']
            messages.success(request, "Archivo subido y usuarios creados exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {str(e)}")
    return render(request, "upload_excel.html", {"base_template": base_template})

