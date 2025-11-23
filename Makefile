.PHONY: help runserver migrate

help:
	@echo "Comandos disponibles:"
	@echo "  make runserver    - Iniciar el servidor de desarrollo"
	@echo "  make migrate      - Aplicar migraciones de base de datos"

runserver:
	uv run python manage.py runserver

migrate:
	uv run python manage.py migrate
