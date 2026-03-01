# ============================================================================
# Stage 1 — Builder
# Install Python dependencies into a virtual environment.
# This stage includes build tools (gcc, libpq-dev) that are NOT copied to
# the runtime stage, keeping the final image lean.
# ============================================================================
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Install only the OS packages needed to compile Python deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Create an isolated virtual environment so we can copy it cleanly
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ============================================================================
# Stage 2 — Runtime
# Lean image with only what's needed to run the application.
# ============================================================================
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Runtime OS deps (libpq for psycopg2 at runtime, curl for HEALTHCHECK)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 curl && \
    rm -rf /var/lib/apt/lists/*

# Copy only the compiled venv from builder — no build tools included
COPY --from=builder /opt/venv /opt/venv

WORKDIR /app

# Copy application source
COPY . .

# ── Non-root user ──────────────────────────────────────────────────────────
# Create a dedicated unprivileged user for the application process.
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-create-home --shell /bin/false appuser && \
    chown -R appuser:appgroup /app

# Collect static files as root (needs write access), then drop privileges
RUN python manage.py collectstatic --noinput 2>/dev/null || true

USER appuser

EXPOSE 8000

# ── Health check ───────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
