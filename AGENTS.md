# AGENTS.md — MedAlert
App web para que un cuidador gestione medicamentos, recordatorios y citas de sus pacientes, con avisos por WhatsApp y reportes PDF.

## Stack y estructura
- Django (en `backend/`): Django 6 + DRF, JWT (simplejwt), SQLite, ReportLab. App principal `medications/`.
- Vue (en `frontend/`): Vue 3 + TypeScript + Vite, Tailwind, Vitest.

## Comandos
- Activar venv (PowerShell, desde la raíz): `.\venv\Scripts\Activate.ps1`
- Tests Django: `python manage.py test` (desde `backend/`)
- Tests Vue: `npm test` (desde `frontend/`)
- Servidores: `python manage.py runserver` (`backend/`) · `npm run dev` (`frontend/`)
- Recordatorios WhatsApp: `python manage.py enviar_recordatorios_whatsapp` (`backend/`)

## Convenciones
- Modelos y clases en inglés (`Reminder`, `Patient`); campos y mensajes en español (`hora`, `fecha_fin`, `activo`).
- Frontend: componentes en `src/components/<dominio>/`, tests en `__tests__/*.spec.ts` junto al código.
- Configuración solo por variables de entorno (`.env`, plantilla en `.env.example`).

## Reglas de dominio / trampas
- El venv está en la raíz (`MedAlert/venv`), no en `backend/`: actívalo antes de entrar en `backend/`.
- Fechas y horas: usa siempre `timezone.localdate()` y `timezone.localtime()`, nunca `date.today()` ni `datetime.now()`. `TIME_ZONE` sale de `DJANGO_TIME_ZONE` (por defecto `America/Bogota`) y `Reminder.hora` es hora local.
- En tests, fija el reloj con `reloj()` de `tests.py` (parchea `django.utils.timezone.now`); el CI corre en UTC.
- Un recordatorio de medicamento no se envía si su `fecha_fin` ya pasó.
- Sin `DJANGO_SECRET_KEY` en `backend/.env`, Django no arranca.

## Forma de trabajar
- Lee MEMORY.md antes de empezar.
- Cambios medianos o grandes: modo plan y aprobación antes de tocar código.
- Al terminar: resume cambios, resultado de los tests y decisiones que deba revisar.

## Límites
- 🚫 Nunca guardar claves ni tokens en el repo.
- ✅ Tests en verde antes de dar algo por hecho.
- ✅ Actualizar MEMORY.md al terminar cada tarea.
