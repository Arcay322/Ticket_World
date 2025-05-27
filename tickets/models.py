from django.db import models

class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    class Meta:
        managed = False
        db_table = 'categorias'

    def __str__(self):
        return self.nombre


class Evento(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha = models.DateTimeField()
    lugar = models.CharField(max_length=200)
    id_categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, db_column='id_categoria')

    class Meta:
        managed = False
        db_table = 'eventos'

    def __str__(self):
        return self.nombre
    


class Boleto(models.Model):
    id = models.AutoField(primary_key=True)
    id_evento = models.ForeignKey(Evento, on_delete=models.CASCADE, db_column='id_evento')
    tipo = models.CharField(max_length=50)  # VIP, General, Preferencial
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_disponible = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'boletos'

    def __str__(self):
        return f"{self.tipo} - {self.id_evento.titulo}"


class MetodoPago(models.Model):
    id = models.AutoField(primary_key=True)
    metodo = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'metodos_pago'

    def __str__(self):
        return self.metodo


class Venta(models.Model):
    id = models.AutoField(primary_key=True)
    id_usuario = models.IntegerField()  # Aquí no mapeamos FK a usuarios de Django porque están en otra DB
    fecha_compra = models.DateTimeField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    id_metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.CASCADE, db_column='id_metodo_pago')

    class Meta:
        managed = False
        db_table = 'ventas'

    def __str__(self):
        return f"Venta {self.id} - Usuario {self.id_usuario} - Total {self.total}"


class DetalleVenta(models.Model):
    id = models.AutoField(primary_key=True)
    id_compra = models.ForeignKey(Venta, on_delete=models.CASCADE, db_column='id_compra')
    id_boleto = models.ForeignKey(Boleto, on_delete=models.CASCADE, db_column='id_boleto')
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'detalle_venta'

    def __str__(self):
        return f"Detalle {self.id} - Venta {self.id_compra.id}"


class Opinion(models.Model):
    id = models.AutoField(primary_key=True)
    id_usuario = models.IntegerField()  # Id del usuario en la otra DB
    id_evento = models.ForeignKey(Evento, on_delete=models.CASCADE, db_column='id_evento')
    calificacion = models.IntegerField()
    comentario = models.TextField()
    fecha_opinion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'opiniones'

    def __str__(self):
        return f"Opinion {self.id} - Evento {self.id_evento.titulo} - Calificación {self.calificacion}"
