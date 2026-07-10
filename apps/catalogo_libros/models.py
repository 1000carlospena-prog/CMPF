from django.db import models


class Autor(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Editora(models.Model):
    nombreEditora = models.CharField(max_length=50)
    ciudad = models.CharField(max_length=50)

    def __str__(self):
        return self.nombreEditora


class Generos(models.Model):
    tipoGenero = models.CharField(max_length=50)

    def __str__(self):
        return self.tipoGenero


class Libros(models.Model):
    nombreLibro = models.CharField(max_length=50)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, null=False)
    genero = models.ForeignKey(Generos, on_delete=models.CASCADE, null=True)
    editora = models.ForeignKey(Editora, on_delete=models.CASCADE, null=False)
    precio = models.DecimalField(max_digits=5, decimal_places=2)
    fechaPublicacion = models.DateField()
    imagen = models.ImageField(upload_to='libros/', blank=True, null=True)
    sinopsis = models.TextField(null=False)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return self.nombreLibro
