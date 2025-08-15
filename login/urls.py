from django.urls import path
from .views import registrar_estudiante, cargar_excel, login_view, subir_reporte, salir, reportes_estudiante, reportes_puesto_puntaje, reportes_observaciones, generar_imagenes_reportes,generar_reporte, lista_estudiantes, editar_estudiante, eliminar_estudiante, agregar_observacion, eliminar_estudiantes_masivo, generar_imagenes_reportes_por_fecha, seleccionar_fecha_generacion, generar_graficos_todos_estudiantes, cargar_asistencias, generar_reporte_asistencia, prueba, generar_todo_reporte, descargar_reporte, descargar_reportes_zip, generar_reporte_asistencia_todos, descargar_reportes_asistencia_zip, actualizar_datos, descargar_estudiantes_excel, ver_asistencias, ver_todas_asistencias, eliminar_asistencia, editar_asistencia, acciones_asistencias, registrar_asistencia, editar_variable_control, asignar_tutores, obtener_estudiantes_tutor, asignar_estudiante, desasignar_estudiante, listar_tutores, crear_tutor, obtener_todos_los_estudiantes, estudiantes_asignados_tutor, reportes_estudiante_tutor, ver_asistencias_tutor, generar_todos_los_reportes, iniciar_tarea_reportes, obtener_estado_tarea, vista_grafico_respuestas, obtener_reportes_resumen, vista_grafico_estudiante, generar_reportes_odf_asistencia, vista_grafico_respuestas_tutor, listar_profesores, crear_profesor, asignar_curso, asignar_cursos_profesor, obtener_cursos_profesor, obtener_todos_los_cursos, desasignar_curso, cursos_por_profesor, obtener_grafico_por_intervalos, vista_grafico_intervalos, fechas_unicas_por_nivel_y_curso, obtener_distribucion_por_fecha, vista_grafico_por_tipo, obtener_grafico_por_tipo, seleccionar_curso, seleccionar_fecha, seleccionar_nivel, subir_imagen_pregunta, evaluacion_simulacros, simulacros, dashboard_reportes, obtener_fechas_nivel, obtener_resultados_fecha, dashboard_reportes1, obtener_resultados_fecha1, dashboard_reportes2

urlpatterns = [

    #Tablas
    path('tabla_resultados2/', dashboard_reportes2, name= 'tabla_resultados1'),
    path('tabla_resultados1/', dashboard_reportes1, name= 'tabla_resultados1'),
    path('tabla_resultados/', dashboard_reportes, name= 'tabla_resultados'),
    path('obtener_fechas_nivel/<str:nivel>/', obtener_fechas_nivel, name= 'fechas_nivel'),
    path('obtener_resultados_fecha/<str:nivel>/<str:fecha>/', obtener_resultados_fecha, name= 'resultados_fechas_nivel'),
    path('obtener_resultados_fecha1/<str:nivel>/<str:fecha>/', obtener_resultados_fecha1, name= 'resultados_fechas_nivel'),
    



    #Simulacros
    path('simulacros/', simulacros, name='simulacros'),




    #preguntas
    path('subir-preguntas/', seleccionar_nivel, name='seleccionar_nivel'),
    path('subir-preguntas/<str:nivel>/', seleccionar_fecha, name='seleccionar_fecha'),
    path('subir-preguntas/<str:nivel>/<str:fecha>/', seleccionar_curso, name='seleccionar_curso'),
    path('subir-preguntas/<str:nivel>/<str:fecha>/<str:curso>/', subir_imagen_pregunta, name='subir_imagen_pregunta'),




    #Cursos
    path("grafico-por-tipo/", vista_grafico_por_tipo, name="grafico_por_tipo"),
    path("api/grafico-por-tipo/", obtener_grafico_por_tipo, name="api_grafico_por_tipo"),
    path("api/fechas-unicas/", fechas_unicas_por_nivel_y_curso, name="fechas_unicas_por_nivel_y_curso"),
    path('cursos-profesor/', cursos_por_profesor, name='cursos_por_profesor'),
    path('grafico-por-intervalos/', vista_grafico_intervalos, name='grafico_por_intervalos'),
    path('api/grafico-intervalos/', obtener_grafico_por_intervalos, name='api_grafico_intervalos'),
    path("api/distribucion-por-fecha/", obtener_distribucion_por_fecha, name="api_distribucion_por_fecha"),
    path("evaluacion_simulacros/", evaluacion_simulacros, name="evaluacion_simulacros"),


    #Profesores
    path('profesores/', listar_profesores, name='listar_profesores'),
    path('crear-profesor/', crear_profesor, name='crear_profesor'),
    path('asignar-cursos/', asignar_cursos_profesor, name='asignar_cursos'),
    path('obtener-cursos-profesor/<int:profesor_id>/', obtener_cursos_profesor, name='obtener_cursos_profesor'),
    path('obtener-todos-cursos/', obtener_todos_los_cursos, name='obtener_todos_los_cursos'),
    path('asignar-curso/', asignar_curso, name='asignar_curso'),
    path('desasignar-curso/', desasignar_curso, name='desasignar_curso'),

    #
    path('iniciar-tarea-reportes/', iniciar_tarea_reportes, name='iniciar_tarea_reportes'),
    path('estado-tarea/<str:task_id>/', obtener_estado_tarea, name='obtener_estado_tarea'),
    path('grafico-respuestas/', vista_grafico_respuestas, name='grafico_respuestas'),
    path("api/reportes-resumen/", obtener_reportes_resumen, name="api_reportes_resumen"),
    path('mi-evolucion/', vista_grafico_estudiante, name='grafico_estudiante'),
    path('evolucion_asignados_a_mi/', vista_grafico_respuestas_tutor, name='graficos_lineas_mis_asignados'),

    #tutores
    path('tutorados/', estudiantes_asignados_tutor, name='tutorados'),
    path('asignar-tutores/', asignar_tutores, name='asignar_tutores'),
    path('obtener-estudiantes/<int:tutor_id>/', obtener_estudiantes_tutor, name='obtener_estudiantes_tutor'),
    path('asignar-estudiante/', asignar_estudiante, name='asignar_estudiante'),
    path('desasignar-estudiante/', desasignar_estudiante, name='desasignar_estudiante'),
    path('tutores/', listar_tutores, name='listar_tutores'),
    path('crear-tutor/', crear_tutor, name='crear_tutor'),
    path('obtener-todos-estudiantes/', obtener_todos_los_estudiantes, name='obtener_todos_estudiantes'),

    path('', reportes_puesto_puntaje, name='home'),
    path('actualizar_datos/', actualizar_datos, name='actualizar_datos'),
    path('cargar_asistencias/', cargar_asistencias, name='subir_asistencia'),
    path('cargar-excel/', cargar_excel, name='cargar_excel'),
    path('descargar-reporte/<int:pk>/', descargar_reporte, name='descargar_reporte'),
    path('descargar-reportes/', descargar_reportes_zip, name='descargar_reportes_zip'),
    path('descargar-asistencias/', descargar_reportes_asistencia_zip, name='descargar_reportes_asistencias_zip'),
    path('descargar_estudiantes_excel/', descargar_estudiantes_excel, name='descargar_estudiantes_excel'),
    path('editar-variable/', editar_variable_control, name='editar_variable_control'),
    path('estudiantes/', lista_estudiantes, name='lista_estudiantes'),
    path('estudiantes/eliminar-masivo/', eliminar_estudiantes_masivo, name='eliminar_estudiantes_masivo'),
    path('estudiantes/<int:estudiante_id>/observaciones/', agregar_observacion, name='agregar_observacion'),
    path('estudiantes/editar/<int:pk>/', editar_estudiante, name='editar_estudiante'),
    path('estudiantes/reporte/<int:pk>/', reportes_estudiante_tutor, name='reporte_estudiante_tutor'),
    path('estudiantes/asistencias/<int:pk>/', ver_asistencias_tutor, name='reporte_asistencias_tutor'),
    path('estudiantes/eliminar/<int:pk>/', eliminar_estudiante, name='eliminar_estudiante'),
    path('generar_imagenes_fecha/', generar_imagenes_reportes_por_fecha, name='generar_imagenes_fecha'),
    path('generar_imagenes_reportes/', generar_imagenes_reportes, name='generar_img_carpetas'),
    path("generar_reporte/", generar_reporte, name="generar_reporte"),
    path('generar_reporte_todos/', generar_reportes_odf_asistencia, name='generar_asistencia_todos'),
    path('generar_todo_reporte/', generar_todo_reporte, name='generar_todo_reporte'),
    path('login/', login_view, name='login'),
    path('observaciones/', reportes_observaciones, name='observaciones'),
    path('prueba/', prueba, name='prueba'),
    path('generar_graficos_todos/', generar_graficos_todos_estudiantes, name='generar_graficos_todos'),
    path('reporte_asistencia/', generar_reporte_asistencia, name='reporte_asistencia'),
    path('registrar/', registrar_estudiante, name='registrar_estudiante'),
    path('reportes_estudiante/', reportes_estudiante, name = 'reportes_estudiante'),
    path('salir/', salir, name='salir'),
    path('seleccionar_fecha_reporte/', seleccionar_fecha_generacion, name='seleccionar_fecha_generacion'),
    path('generar_todos_reportes/', generar_todos_los_reportes, name='generar_todos_los_reportes'),
    path('subir_reporte/', subir_reporte, name='subir_reporte'),
    path('mis-asistencias/', ver_asistencias, name='ver_asistencias'),
    path('listar_asistencias/', ver_todas_asistencias, name='listar_asistencias'),
    path('asistencias/eliminar/<int:pk>/', eliminar_asistencia, name='eliminar_asistencia'),
    path('asistencias/editar/<int:pk>/', editar_asistencia, name='editar_asistencia'),
    path('asistencias/acciones/', acciones_asistencias, name='acciones_asistencias'),
    path('registrar_asistencias/', registrar_asistencia, name='registrar_asistencia'),
]