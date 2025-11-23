FROM python:3.11.14-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install system dependencies (only for WeasyPrint PDF generation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Install uv in a separate location to avoid conflicts with .venv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (production group included)
# UV_PROJECT_ENVIRONMENT sets where uv installs packages
# We use /usr/local to install system-wide and avoid .venv conflicts
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --group production

# Copy application code
COPY . .

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/mediafiles

# Collect static files
RUN uv run python manage.py collectstatic --noinput --clear

# Create a non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Run gunicorn with uv
CMD ["uv", "run", "gunicorn", "--config", "gunicorn.conf.py", "libre_lims.wsgi:application"]
