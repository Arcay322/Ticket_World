# Generated by Django 5.2 on 2025-06-15 07:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0009_alter_notification_options_notification_dismissed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitudproveedor',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='solicitudes_proveedor_recibidas', to=settings.AUTH_USER_MODEL, verbose_name='Usuario Solicitante'),
        ),
    ]
