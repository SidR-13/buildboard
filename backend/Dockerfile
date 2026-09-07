# Platform is pinned in the FROM rather than passed at build time on purpose: this image only
# ever runs on one x86_64 EC2 host, and building it on an arm64 Mac must not produce an arm image.
# Docker's linter flags this as non-portable, which is right in general and wrong for this deploy.
FROM --platform=linux/amd64 python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM --platform=linux/amd64 python:3.11-slim
WORKDIR /app
# Runs as a non-root user, not root's default in this base image - a container-escape or
# dependency RCE then only has appuser's permissions, not root's.
RUN useradd --create-home --shell /bin/bash appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
RUN chown -R appuser:appuser /app /home/appuser/.local
USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
