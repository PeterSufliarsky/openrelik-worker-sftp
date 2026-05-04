# Use the official Docker Hub alpine base image
FROM alpine:3.23

# Install the latest uv binaries
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Configure debugging
ARG OPENRELIK_PYDEBUG
ENV OPENRELIK_PYDEBUG=${OPENRELIK_PYDEBUG:-0}
ARG OPENRELIK_PYDEBUG_PORT
ENV OPENRELIK_PYDEBUG_PORT=${OPENRELIK_PYDEBUG_PORT:-5678}

# Create a user and group
RUN addgroup openrelik
RUN adduser -S openrelik -G openrelik -h /openrelik

# Set working directory
WORKDIR /openrelik

# Run as non-root user
USER openrelik

# Copy poetry toml and install dependencies
COPY uv.lock pyproject.toml .

# Install the project's dependencies using the lockfile and settings
RUN uv sync --locked --no-install-project --no-dev

# Copy project files
COPY . ./

# Installing separately from its dependencies allows optimal layer caching
# RUN uv sync --locked --no-dev

# Install the worker and set environment to use the correct python interpreter.
ENV PATH="/openrelik/.venv/bin:$PATH"

# Default command if not run from docker-compose (and command being overidden)
CMD ["celery", "--app=src.tasks", "worker", "--task-events", "--concurrency=1", "--loglevel=DEBUG"]
