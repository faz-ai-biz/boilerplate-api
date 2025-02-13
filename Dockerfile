# Build stage
FROM python:3.11-slim-bookworm as builder

WORKDIR /build

# Install build dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim-bookworm

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Install OS dependencies
RUN apt-get update && \
    apt-get install -y netcat-traditional postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=prod
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy the project files into the container
COPY . .

# Copy .env to src/.env
RUN cp env.prod ./src/.env

# Set ownership and switch to non-root user
RUN chown -R appuser:appuser /app/src


USER appuser


# Fix permissions and line endings for scripts
RUN find /app/devops/scripts -type f -name "*.sh" -exec chmod +x {} \; && \
    find /app/devops/scripts -type f -name "*.sh" -exec sed -i 's/\r$//' {} \;

# Add version and build information
ARG VERSION
ARG BUILD_DATE
ARG GIT_COMMIT
LABEL org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${GIT_COMMIT}"
