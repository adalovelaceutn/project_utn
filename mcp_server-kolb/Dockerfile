FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src

RUN pip install --no-cache-dir -e .

EXPOSE 8080

CMD ["uvicorn", "kolb_profile_server.server:asgi_app", "--host", "0.0.0.0", "--port", "8080"]
