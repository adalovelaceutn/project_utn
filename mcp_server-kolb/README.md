# kolb-profile-server

Servidor MCP en Python con transporte HTTP streameable.

## Requisitos

- Python 3.12+

## Configuracion inicial

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Ejecutar servidor MCP (HTTP streameable)

```bash
kolb-profile-server
```

Variables de entorno opcionales:

- `KOLB_SERVER_HOST` (default: `0.0.0.0`)
- `KOLB_SERVER_PORT` (default: `8080`)
- `KOLB_SERVER_PATH` (default: `/mcp`)

## Estructura

- `src/kolb_profile_server/server.py`: bootstrap del servidor MCP.
- `src/kolb_profile_server/tools/health.py`: herramientas iniciales.
- `.vscode/settings.json`: interprete y autoactivacion de `.venv`.
