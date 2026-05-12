# Kolb Frontend

Aplicación Angular (`@angular/latest`) conectada a la API en `data/`.

## Funcionalidades

- Angular Material para UI.
- Login contra `POST /api/v1/auth/login`.
- Registro de usuario si no existe.
- Dashboard con 3 componentes:
	- Datos del usuario.
	- Perfil Kolb.
	- Chat asistente.
- Persistencia del perfil Kolb asociado al usuario autenticado.

## Requisitos

- Node 20+
- API FastAPI corriendo en `http://localhost:8000`

## Ejecutar

```bash
cd /workspaces/project_utn/frontend/kolb-frontend
npm install
npm start
```

Abrir `http://localhost:4200`.

## Build

```bash
npm run build
```
