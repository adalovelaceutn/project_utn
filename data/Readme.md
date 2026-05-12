## API REST Kolb (FastAPI + MongoDB)

Esta carpeta contiene una API REST completa para persistir el perfil Kolb de alumnos en MongoDB.

### Requisitos

- Python 3.11+
- Docker y Docker Compose

### 1) Crear entorno virtual

```bash
cd /workspaces/project_utn/data
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2) Configurar variables de entorno

```bash
cp .env.example .env
```

Variables principales:

- `MONGO_URI`: URI de MongoDB
- `MONGO_DB_NAME`: nombre de base de datos
- `MONGO_KOLB_COLLECTION`: colección de perfiles Kolb
- `MONGO_USERS_COLLECTION`: colección de usuarios
- `API_HOST`: host de FastAPI
- `API_PORT`: puerto de FastAPI
- `AUTH_SECRET_KEY`: clave para firmar JWT
- `AUTH_ALGORITHM`: algoritmo JWT
- `AUTH_ACCESS_TOKEN_EXPIRE_MINUTES`: expiración del token

### 3) Levantar MongoDB con persistencia en `data/data`

```bash
docker compose up -d
```

MongoDB persistirá datos en:

- `./data` (dentro de esta carpeta, es decir `data/data` del repo)

### 4) Ejecutar API

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Documentación interactiva:

- `http://localhost:8000/docs`

### Endpoints principales

- `GET /health`
- `POST /api/v1/auth/login`
- `POST /api/v1/users`
- `GET /api/v1/users`
- `GET /api/v1/users/{user_id}`
- `PATCH /api/v1/users/{user_id}`
- `PUT /api/v1/users/{user_id}`
- `DELETE /api/v1/users/{user_id}`
- `POST /api/v1/kolb-profiles`
- `GET /api/v1/kolb-profiles`
- `GET /api/v1/kolb-profiles/{profile_id}`
- `GET /api/v1/kolb-profiles/by-dni/{dni}`
- `GET /api/v1/kolb-profiles/by-user/{user_id}`
- `PUT /api/v1/kolb-profiles/{profile_id}`
- `PATCH /api/v1/kolb-profiles/{profile_id}`
- `DELETE /api/v1/kolb-profiles/{profile_id}`

Regla de negocio:

- Cada perfil Kolb debe pertenecer a un usuario existente mediante su `dni`.

### Ejemplo de payload de creación

```json
{
	"dni": "18447836",
	"puntajes": {
		"experiencia_concreta": 70,
		"observacion_reflexiva": 60,
		"conceptualizacion_abstracta": 80,
		"experimentacion_activa": 65
	},
	"confidence_score": 0.78,
	"interview_responses": []
}
```

### Parar MongoDB

```bash
docker compose down
```

