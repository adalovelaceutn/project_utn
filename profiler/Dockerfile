FROM python:3.12-slim

WORKDIR /app

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY src/ ./src/
COPY pyproject.toml ./

# Install runtime deps and package
RUN pip install --no-cache-dir -e .

EXPOSE 8001

ENV PYTHONUNBUFFERED=1

CMD ["kolb-profiler"]
