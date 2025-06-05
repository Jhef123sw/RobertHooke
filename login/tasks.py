# login/tasks.py

from celery import shared_task
from datetime import datetime
from .models import Estudiante, Reporte
import os
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import pandas as pd
import math

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
def generar_imagenes_reportes_por_fecha_task(fecha_str):
    try:
        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        cursos = [
            "Razonamiento Verbal", "Razonamiento Matemático", "Aritmética", "Álgebra",
            "Geometría", "Trigonometría", "Física", "Química", "Biología", "Lenguaje",
            "Literatura", "Historia", "Geografía", "Filosofía", "Psicología", "Economía"
        ]

        ruta_base = os.path.join(settings.MEDIA_ROOT)

        for estudiante in Estudiante.objects.all():
            reportes = Reporte.objects.filter(KK_usuario=estudiante, fecha_de_examen=fecha_obj, reporte_actualizado = True)

            for reporte in reportes:
                datos = reporte.obtener_datos()
                nivel = reporte.nivel

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

                    nombre_archivo = f"{curso}_{estudiante.usuario}_{reporte.fecha_de_examen}.png".replace(" ", "_")
                    ruta_archivo = os.path.join(carpeta_usuario, nombre_archivo)
                    estudiante.reporte_actualizado = False
                    estudiante.save()
                    plt.savefig(ruta_archivo, format='png', bbox_inches='tight', facecolor='white')
                    plt.close(fig)
        
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
        "Geometría": v.Geom_Sem if nivel == 30 else v.Geom_Pre,
        "Trigonometría": v.Trig_Sem if nivel == 30 else v.Trig_Pre,
        "Física": v.Fi_Sem if nivel == 30 else v.Fi_Pre,
        "Química": v.Qui_Sem if nivel == 30 else v.Qui_Pre,
        "Biología": v.Bio_Sem if nivel == 30 else v.Bio_Pre,
        "Lenguaje": v.Le_Sem if nivel == 30 else v.Le_Pre,
        "Literatura": v.Lit_Sem if nivel == 30 else v.Lit_Pre,
        "Historia": v.Hi_Sem if nivel == 30 else v.Hi_Pre,
        "Geografía": v.Geog_Sem if nivel == 30 else v.Geog_Pre,
        "Filosofía": v.Fil_Sem if nivel == 30 else v.Fil_Pre,
        "Psicología": v.Psi_Sem if nivel == 30 else v.Psi_Pre,
        "Economía": v.Ec_Sem if nivel == 30 else v.Ec_Pre,
    }

    return cursos