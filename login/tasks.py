# login/tasks.py

from celery import shared_task, states
from celery.exceptions import Ignore
from datetime import datetime
from .models import Estudiante, Reporte, Asistencia
import os
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import pandas as pd
import math
from collections import defaultdict
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from io import BytesIO


@shared_task(bind=True)
def generar_reportes_completos_task(self):
    try:
        self.update_state(state='PROGRESO', meta={'step': 'Generando reportes', 'progress': 20})
        generar_todo_reporte_task()

        self.update_state(state='PROGRESO', meta={'step': 'Generando gráficos', 'progress': 60})
        generar_imagenes_reportes_por_fecha_task()

        self.update_state(state='PROGRESO', meta={'step': 'Finalizando', 'progress': 90})

        return {'status': 'Completado', 'progress': 100}
    except Exception as e:
        self.update_state(state=states.FAILURE, meta={'exc': str(e)})
        raise Ignore()
    resultado1 = generar_todo_reporte_task()
    resultado2 = generar_imagenes_reportes_por_fecha_task()
    return f"{resultado1} | {resultado2}"

cursos_pre = [
            "Razonamiento Verbal", "Razonamiento Matemático", "Aritmética", "Álgebra",
            "Geometría", "Trigonometría", "Física", "Química", "Biología", "Lenguaje",
            "Literatura", "Historia", "Geografía", "Filosofía", "Psicología", "Economía"
        ]

@shared_task
def generar_todo_reporte_task():
    try:
        estudiantes = Estudiante.objects.filter(reporte_actualizado=True)
        ruta_guardar = os.path.join(settings.MEDIA_ROOT, 'reportes/simulacros')
        plantilla_pre = os.path.join(settings.BASE_DIR, "login/static/img/plantilla-notas-pre.png")
        plantilla_sem = os.path.join(settings.BASE_DIR, "login/static/img/plantilla-notas-semillas.png")
        if not os.path.exists(plantilla_pre):
            raise FileNotFoundError("No se encontró la plantilla del reporte para pre.")
        elif not os.path.exists(plantilla_sem):
            raise FileNotFoundError("No se encontró la plantilla del reporte para semillero.")
        for estudiante in estudiantes:
            reportes_qs = estudiante.reportes.all().order_by('-fecha_de_examen')
            if not reportes_qs.exists():
                continue

            reportes = list(reportes_qs[:8][::-1])  # últimos 8, orden cronológico

            ruta_carpeta = os.path.join(settings.MEDIA_ROOT, f'{estudiante.usuario}_2025/imagenes_reporte/')
            os.makedirs(ruta_carpeta, exist_ok=True)

            # Cursos y preguntas por curso según nivel
            nivel = reportes[0].nivel
            cursos = cursos_pre
            preguntas_por_curso = obtener_preguntas_por_curso(nivel)


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

            for curso, datos in datos_por_curso.items():
                crear_grafico_estudiante_curso(estudiante, curso, datos)

            # Puntaje general
            fechas = [r.fecha_de_examen.strftime('%Y-%m-%d') for r in reportes]
            puntajes = [r.obtener_total_puntaje() for r in reportes]

            def generar_grafico_puntaje_barras(x, y):
                fig, ax = plt.subplots(figsize=(6, 3))
                barras = ax.bar(x, y, color='#DA880B')
                
                for spine in ax.spines.values():
                    spine.set_visible(False)
                
                for barra, valor in zip(barras, y):
                    altura = barra.get_height()
                    ax.text(
                        barra.get_x() + barra.get_width() / 2,
                        altura + 1,
                        f'{valor:.2f}',  # <- redondea a 2 decimales
                        ha='center',
                        va='bottom',
                        fontsize=13,
                        fontweight='bold'
                    )
                
                plt.xticks(rotation=0, fontsize=8)
                ax.tick_params(axis='y', left=False, labelleft=False)
                ax.grid(False)
                
                ruta_grafico = os.path.join(ruta_carpeta, "zgrafico_puntaje.png")
                fig.tight_layout()
                fig.savefig(ruta_grafico, bbox_inches='tight')
                plt.close(fig)
                return ruta_grafico

            ruta_grafico_puntaje = generar_grafico_puntaje_barras(fechas, puntajes)

            # Crear imagen final
            if nivel == 30:
                plantilla = Image.open(plantilla_sem)
            else:
                plantilla = Image.open(plantilla_pre)
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
            estudiante.reporte_actualizado = False
            estudiante.save()
            plantilla.save(resultado_path)

        return "Reportes generados correctamente."

    except Exception as e:
        return f"Error: {str(e)}"

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
    cols = 4
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

@shared_task
def generar_imagenes_reportes_por_fecha_task():
    try:
        cursos = [
            "Razonamiento Verbal", "Razonamiento Matemático", "Aritmética", "Álgebra",
            "Geometría", "Trigonometría", "Física", "Química", "Biología", "Lenguaje",
            "Literatura", "Historia", "Geografía", "Filosofía", "Psicología", "Economía"
        ]

        ruta_base = os.path.join(settings.MEDIA_ROOT)

        reportes = Reporte.objects.filter(reporte_actualizado=True)

        for reporte in reportes:
            estudiante = reporte.KK_usuario
            datos = reporte.obtener_datos()
            nivel = reporte.nivel
            fecha_examen = reporte.fecha_de_examen

            preguntas_por_curso = obtener_preguntas_por_curso(nivel)

            carpeta_usuario = os.path.join(ruta_base, f"{estudiante.usuario}_2025")
            os.makedirs(carpeta_usuario, exist_ok=True)

            for curso, valores in datos.items():
                correctas, incorrectas = valores
                total_preguntas = preguntas_por_curso.get(curso, 10)
                en_blanco = total_preguntas - (correctas + incorrectas)

                etiquetas = ["Correctas", "Incorrectas", "En blanco"]
                valores_barras = [correctas, incorrectas, en_blanco]
                colores = ["green", "red", "gray"]

                fig, ax = plt.subplots(figsize=(8, 4))
                barras = ax.bar(etiquetas, valores_barras, color=colores)

                for barra in barras:
                    altura = barra.get_height()
                    ax.annotate(f'{altura}',
                                xy=(barra.get_x() + barra.get_width() / 2, altura),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom',
                                fontsize=15)

                ax.set_title("")
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.tick_params(left=False, bottom=False)
                ax.set_yticks([])

                plt.tight_layout()

                nombre_archivo = f"{curso}_{estudiante.usuario}_{fecha_examen}.png".replace(" ", "_")
                ruta_archivo = os.path.join(carpeta_usuario, nombre_archivo)

                plt.savefig(ruta_archivo, format='png', bbox_inches='tight', facecolor='white')
                plt.close(fig)

            # Marcar como procesado
            reporte.reporte_actualizado = False
            reporte.save()

        return "Imágenes generadas correctamente."

    except Exception as e:
        return f"Error generando imágenes: {str(e)}"

def obtener_preguntas_por_curso(nivel):
    from login.models import VariableControl

    try:
        v = VariableControl.objects.get(ID_Variable=1)
    except VariableControl.DoesNotExist:
        return {}

    # Estructura: curso → cantidad según nivel
    cursos = {
        "Razonamiento Verbal": v.Rv_Sem if nivel == 30 else v.Rv_Pre,
        "Razonamiento Matemático": v.Rm_Sem if nivel == 30 else v.Rm_Pre,
        "Aritmética": v.Ar_Sem if nivel == 30 else v.Ar_Pre,
        "Álgebra": v.Al_Sem if nivel == 30 else v.Al_Pre,
        "Geometría": v.Ge_Sem if nivel == 30 else v.Ge_Pre,
        "Trigonometría": v.Tr_Sem if nivel == 30 else v.Tr_Pre,
        "Física": v.Fi_Sem if nivel == 30 else v.Fi_Pre,
        "Química": v.Qu_Sem if nivel == 30 else v.Qu_Pre,
        "Biología": v.Bi_Sem if nivel == 30 else v.Bi_Pre,
        "Lenguaje": v.Le_Sem if nivel == 30 else v.Le_Pre,
        "Literatura": v.Lit_Sem if nivel == 30 else v.Lit_Pre,
        "Historia": v.Hi_Sem if nivel == 30 else v.Hi_Pre,
        "Geografía": v.Gf_Sem if nivel == 30 else v.Gf_Pre,
        "Filosofía": v.Fil_Sem if nivel == 30 else v.Fil_Pre,
        "Psicología": v.Psi_Sem if nivel == 30 else v.Psi_Pre,
        "Economía": v.Ec_Sem if nivel == 30 else v.Ec_Pre,
    }

    return cursos

def generar_pdfs_asistencias_por_estudiante_task(asistencias_queryset):
    carpeta = os.path.join(settings.MEDIA_ROOT, "reportes", "asistencias")
    os.makedirs(carpeta, exist_ok=True)

    # Agrupamos asistencias por usuario
    asistencias_por_usuario = defaultdict(list)
    for a in asistencias_queryset.order_by('KK_usuario__usuario', 'Fecha', 'Hora'):
        asistencias_por_usuario[a.KK_usuario.usuario].append(a)

    for usuario, asistencias_usuario in asistencias_por_usuario.items():
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=landscape(A4))
        width, height = landscape(A4)

        def dibujar_encabezado(y_pos):
            p.setFont("Helvetica-Bold", 14)
            p.drawString(30, height - 40, f"Reporte de Asistencias - {usuario}")

            headers = ["Usuario", "Nombre", "Fecha", "Hora", "Nro Marca", "Modalidad", "Observación"]
            x_positions = [30, 80, 310, 390, 470, 550, 650]
            p.setFont("Helvetica-Bold", 10)
            for i, header in enumerate(headers):
                p.drawString(x_positions[i], y_pos, header)
            return y_pos - 25

        y = dibujar_encabezado(height - 80)
        p.setFont("Helvetica", 10)

        # Agrupamos por (usuario, fecha) para asignar Nro Marca
        agrupadas = defaultdict(list)
        for a in asistencias_usuario:
            clave = (a.KK_usuario.usuario, a.Fecha)
            agrupadas[clave].append(a)

        for grupo in agrupadas.values():
            for i, a in enumerate(grupo, start=1):
                datos = [
                    a.KK_usuario.usuario,
                    a.KK_usuario.nombre,
                    a.Fecha.strftime('%d/%m/%Y'),
                    a.Hora,
                    "ENTRADA" if i in [1, 3] else "SALIDA",
                    a.Modalidad,
                    a.Observacion or "-"
                ]
                x_positions = [30, 80, 310, 390, 470, 550, 650]
                for j, valor in enumerate(datos):
                    p.drawString(x_positions[j], y, str(valor))
                y -= 20

                if y < 40:
                    p.showPage()
                    y = dibujar_encabezado(height - 50)
                    p.setFont("Helvetica", 10)

        p.save()
        buffer.seek(0)

        # Guardamos el archivo
        nombre_archivo = f"{usuario}_reporte_asistencia.pdf"
        ruta_archivo = os.path.join(carpeta, nombre_archivo)
        with open(ruta_archivo, 'wb') as f:
            f.write(buffer.getbuffer())