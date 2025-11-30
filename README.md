# libre-lims

Aplicación Django para gestión de pacientes.

## Requisitos

- Python 3.11
- PostgreSQL
- uv (gestor de paquetes)

## Instalación

1. Clonar el repositorio

2. Instalar dependencias:
```bash
uv sync
```

3. Configurar variables de entorno:
Copiar `.env.example` a `.env` y configurar la URL de la base de datos:
```bash
cp .env.example .env
```

Editar `.env` con tu configuración de PostgreSQL:
```
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/libre-lims
```

4. Ejecutar migraciones:
```bash
uv run python manage.py migrate
```

5. Crear superusuario:
```bash
uv run python manage.py createsuperuser
```

6. Ejecutar servidor de desarrollo:
```bash
uv run python manage.py runserver
```

## Licencia

Este proyecto está licenciado bajo la **Apache License 2.0**.

Esto significa que puedes:
- Usar el software para cualquier propósito (comercial o no)
- Modificar el código fuente
- Distribuir el software original o modificado
- Sublicenciar el software

Bajo las siguientes condiciones:
- Debes incluir una copia de la licencia Apache 2.0
- Debes indicar los cambios realizados al código original
- Incluye protección explícita de patentes

Para más detalles, consulta el archivo [LICENSE](LICENSE).
