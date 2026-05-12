# Deploy en Render como Web Service unico (testing)

Este modo evita Blueprint (pago) y corre todo en un solo contenedor:

- Data API (FastAPI)
- MCP server
- Profiler
- Main agent
- Frontend estatico con Nginx

MongoDB en este modo debe ser externo (por ejemplo MongoDB Atlas).

## Archivo de build

Usar [Dockerfile.render-web](Dockerfile.render-web).

## Configuracion en Render

1. New + -> Web Service
2. Connect repo: project_utn
3. Environment: Docker
4. Dockerfile Path: Dockerfile.render-web
5. Branch: main

## Variables de entorno recomendadas

- AUTH_SECRET_KEY: clave JWT fuerte
- MONGO_URI: URI de Mongo externa
- HF_TOKEN: token de Hugging Face
- HF_MODEL_ID (opcional)
- HF_MAX_NEW_TOKENS (opcional)
- HF_TEMPERATURE (opcional)
- TAVILY_API_KEY (opcional)
- TAVILY_BASE_URL (opcional)

No hace falta setear PORT manualmente (Render lo inyecta).

## URLs internas en este modo

Todas por localhost dentro del contenedor:

- API data: http://127.0.0.1:8000
- MCP: http://127.0.0.1:8080/mcp
- Profiler: http://127.0.0.1:8001
- Main: http://127.0.0.1:8002

## Consideraciones

- Este modo es solo para testing.
- Si falla un proceso, se cae todo el servicio.
- Requiere una instancia Mongo externa accesible desde Render.
