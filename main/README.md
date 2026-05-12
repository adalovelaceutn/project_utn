# Main Agent

Orquestador LangGraph para la entrevista Kolb.

Interfaces:

- `POST /chat`: endpoint HTTP que consume el frontend.
- Cliente A2A hacia `profiler/`: delega la entrevista y devuelve cada turno al frontend.

## Variables de entorno

Usa `.env` o `.env.example`.

## Ejecucion local

```bash
cd /workspaces/project_utn/main
/workspaces/project_utn/data/.venv/bin/python -m uvicorn kolb_main.server:app --host 0.0.0.0 --port 8002
```