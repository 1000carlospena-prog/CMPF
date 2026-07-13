from django.db import migrations
from django.utils.text import slugify


def migrate_libros_to_productos(apps, schema_editor):
    Libros = apps.get_model('catalogo_libros', 'Libros')
    Autor = apps.get_model('catalogo_libros', 'Autor')
    Generos = apps.get_model('catalogo_libros', 'Generos')
    Editora = apps.get_model('catalogo_libros', 'Editora')
    Producto = apps.get_model('productos', 'Producto')
    ProductoImagen = apps.get_model('productos', 'ProductoImagen')
    Categoria = apps.get_model('productos', 'Categoria')

    cat_libros, _ = Categoria.objects.get_or_create(
        nombre='Libros', slug='libros',
        defaults={'descripcion': 'Libros y literatura', 'activa': True}
    )

    for libro in Libros.objects.all().select_related('autor', 'genero', 'editora'):
        slug = slugify(libro.nombreLibro)
        autor_str = f'{libro.autor.nombre} {libro.autor.apellido}' if libro.autor else ''
        genero_str = libro.genero.tipoGenero if libro.genero else ''
        editora_str = f'{libro.editora.nombreEditora} ({libro.editora.ciudad})' if libro.editora else ''

        metadata = {
            'autor': autor_str,
            'genero': genero_str,
            'editora': editora_str,
            'fechaPublicacion': str(libro.fechaPublicacion) if libro.fechaPublicacion else '',
            'sinopsis': libro.sinopsis or '',
        }

        descripcion = libro.sinopsis or f'Libro de {autor_str}. Género: {genero_str}.'
        if len(descripcion) > 500:
            descripcion = descripcion[:500]

        prod, created = Producto.objects.get_or_create(
            slug=slug,
            defaults=dict(
                categoria=cat_libros,
                tipo='libro',
                nombre=libro.nombreLibro,
                descripcion=descripcion,
                precio=libro.precio,
                precio_oferta=None,
                existencia=1,
                disponible=libro.disponible,
                destacado=False,
                metadata=metadata,
            )
        )
        if created and libro.imagen:
            ProductoImagen.objects.get_or_create(
                producto=prod, orden=0,
                defaults={'imagen': libro.imagen.name, 'url_externa': ''}
            )


def reverse_migrate(apps, schema_editor):
    Producto = apps.get_model('productos', 'Producto')
    Producto.objects.filter(tipo='libro').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo_libros', '0002_alter_libros_imagen'),
        ('productos', '0005_producto_metadata'),
    ]

    operations = [
        migrations.RunPython(migrate_libros_to_productos, reverse_migrate),
    ]
