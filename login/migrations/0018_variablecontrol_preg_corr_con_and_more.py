# Generated by Django 5.1.3 on 2025-06-04 23:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0017_estudiante_tutor_alter_estudiante_tipo_estudiante'),
    ]

    operations = [
        migrations.AddField(
            model_name='variablecontrol',
            name='Preg_Corr_Con',
            field=models.IntegerField(default=6),
        ),
        migrations.AddField(
            model_name='variablecontrol',
            name='Preg_Corr_Raz',
            field=models.IntegerField(default=8),
        ),
        migrations.AddField(
            model_name='variablecontrol',
            name='Preg_Inc_Con',
            field=models.IntegerField(default=0.51),
        ),
        migrations.AddField(
            model_name='variablecontrol',
            name='Preg_Inc_Raz',
            field=models.IntegerField(default=0.51),
        ),
    ]
