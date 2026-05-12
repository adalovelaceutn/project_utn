# Deploy en Render

Este proyecto queda preparado para despliegue con un unico punto de entrada publico: frontend en el servicio frontend.

Se incluye blueprint de Render en [render.yaml](render.yaml).

## Arquitectura de red

- Publico:
  - frontend (Nginx + Angular) en puerto 8080.
- Interno (servicios privados de Render):
  - data-api en http://data-api:8000
  - main-agent en http://main-agent:8002
  - profiler en http://profiler:8001
  - mcp-server en http://mcp-server:8080
  - mongodb en mongodb:27017

El frontend enruta internamente:

- /api/* -> data-api:8000
- /main-api/* -> main-agent:8002/*

Esto evita CORS en produccion porque el navegador solo ve un dominio publico.

## Variables de entorno recomendadas en Render

Definir al menos:

- AUTH_SECRET_KEY: clave JWT fuerte
- HF_TOKEN: token de Hugging Face Router
- HF_MODEL_ID (opcional, default: Qwen/Qwen2.5-7B-Instruct)
- HF_MAX_NEW_TOKENS (opcional)
- HF_TEMPERATURE (opcional)
- TAVILY_API_KEY (opcional para enriquecer respuestas)
- TAVILY_BASE_URL (opcional, default: https://api.tavily.com)

## Comandos locales de prueba

```bash
docker compose up -d --build
docker compose ps
```

Frontend:

- http://localhost:8080

## Nota importante sobre Render

Render no ejecuta varios servicios dentro de un solo contenedor compartido de forma nativa.
La equivalencia de produccion correcta es: 1 servicio web publico (frontend) + servicios privados internos para backend y base de datos, todos definidos en el mismo blueprint render.yaml.

## Notas de paso de desarrollo a produccion

- Se elimina `ng serve`; frontend se compila y sirve estatico con Nginx.
- Se eliminan URLs localhost hardcodeadas para la comunicacion entre servicios.
- Solo el frontend publica puerto al host.
- Mongo usa volumen persistente `mongo_data`.
