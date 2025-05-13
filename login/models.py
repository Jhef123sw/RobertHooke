from django.db import models

class Estudiante(models.Model):
    PERMISOS_USUARIO = [
        ('estudiante', 'Estudiante'), ('administrador', 'Administrador'),
    ]
    ID_Estudiante = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    usuario = models.CharField(max_length=150, unique=True)
    contraseña = models.CharField(max_length=255)
    tipo_estudiante = models.CharField(max_length=20, choices=PERMISOS_USUARIO, default= "estudiante")
    is_active = models.BooleanField(default=True)  # Atributo requerido
    is_staff = models.BooleanField(default=False)  # Atributo requerido
    last_login = models.DateTimeField(null=True, blank=True)  # Campo requerido
    
    def __str__(self):
        return self.usuario

    @property
    def is_authenticated(self):
        return True  # Siempre devuelve True para usuarios autenticados

class Reporte(models.Model):
    NIVEL_CHOICES = [
        (30, 'Semillero'),
        (90, 'Pre'),
    ]
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES, default=90)
    IDReporte = models.AutoField(primary_key=True)
    KK_usuario = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='reportes')
    Rv_1 = models.IntegerField()
    Rv_2 = models.IntegerField()
    Rm_1 = models.IntegerField()
    Rm_2 = models.IntegerField()
    Ar_1 = models.IntegerField()
    Ar_2 = models.IntegerField()
    Al_1 = models.IntegerField()
    Al_2 = models.IntegerField()
    Ge_1 = models.IntegerField()
    Ge_2 = models.IntegerField()
    Tr_1 = models.IntegerField()
    Tr_2 = models.IntegerField()
    Fi_1 = models.IntegerField()
    Fi_2 = models.IntegerField()
    Qu_1 = models.IntegerField()
    Qu_2 = models.IntegerField()
    Bi_1 = models.IntegerField()
    Bi_2 = models.IntegerField()
    Le_1 = models.IntegerField()
    Le_2 = models.IntegerField()
    Lit_1 = models.IntegerField()
    Lit_2 = models.IntegerField()
    Hi_1 = models.IntegerField()
    Hi_2 = models.IntegerField()
    Gf_1 = models.IntegerField()
    Gf_2 = models.IntegerField()
    Fil_1 = models.IntegerField()
    Fil_2 = models.IntegerField()
    Psi_1 = models.IntegerField()
    Psi_2 = models.IntegerField()
    Ec_1 = models.IntegerField()
    Ec_2 = models.IntegerField()
    fecha_de_examen = models.DateField()
    Observacion =models.CharField(max_length=200)
    puesto = models.IntegerField()

    def obtener_datos(self):
        """Devuelve los datos de cada materia en un diccionario"""
        return {
            "Razonamiento Verbal": (self.Rv_1, self.Rv_2),
            "Razonamiento Matemático": (self.Rm_1, self.Rm_2),
            "Aritmética": (self.Ar_1, self.Ar_2),
            "Álgebra": (self.Al_1, self.Al_2),
            "Geometría": (self.Ge_1, self.Ge_2),
            "Trigonometría": (self.Tr_1, self.Tr_2),
            "Física": (self.Fi_1, self.Fi_2),
            "Química": (self.Qu_1, self.Qu_2),
            "Biología": (self.Bi_1, self.Bi_2),
            "Lenguaje": (self.Le_1, self.Le_2),
            "Literatura": (self.Lit_1, self.Lit_2),
            "Historia": (self.Hi_1, self.Hi_2),
            "Geografía": (self.Gf_1, self.Gf_2),
            "Filosofía": (self.Fil_1, self.Fil_2),
            "Psicología": (self.Psi_1, self.Psi_2),
            "Economía": (self.Ec_1, self.Ec_2),
        }

    def __str__(self):
        return f"Reporte {self.IDReporte} - {self.KK_usuario.usuario}"

    def obtener_total_puntaje(self):
        """Calcula el puntaje total según la fórmula dada"""
        total_correctas = sum([
            self.Rv_1, self.Rm_1, self.Ar_1, self.Al_1, self.Ge_1, self.Tr_1,
            self.Fi_1, self.Qu_1, self.Bi_1, self.Le_1, self.Lit_1, self.Hi_1,
            self.Gf_1, self.Fil_1, self.Psi_1, self.Ec_1
        ])

        total_incorrectas = sum([
            self.Rv_2, self.Rm_2, self.Ar_2, self.Al_2, self.Ge_2, self.Tr_2,
            self.Fi_2, self.Qu_2, self.Bi_2, self.Le_2, self.Lit_2, self.Hi_2,
            self.Gf_2, self.Fil_2, self.Psi_2, self.Ec_2
        ])

        return (7 * total_correctas) - (1.5 * total_incorrectas)
    
class Asistencia(models.Model):
    ID_Reporte = models.AutoField(primary_key=True)
    KK_usuario = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='asistencia')
    Fecha = models.DateField()
    Ingreso_mana = models.CharField(max_length=5, default= "NM")
    Salida_mana = models.CharField(max_length=5, default= "NM")
    Ingreso_tarde = models.CharField(max_length=5, default= "NM")
    Salida_tarde = models.CharField(max_length=5, default= "NM")
    Ingreso_noche = models.CharField(max_length=5, default= "NM")
    Salida_noche = models.CharField(max_length=5, default= "NM")
    Observacion = models.CharField(max_length=30, default= "NM")
