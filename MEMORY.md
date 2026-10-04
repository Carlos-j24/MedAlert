# MEMORY.md — MedAlert
Memoria del proyecto entre sesiones. Máximo ~50 líneas: resume o elimina lo que ya no aporte.

## Estado actual
- v1.0 funcionando: cuidadores, pacientes, medicamentos, recordatorios, citas, WhatsApp (CallMeBot) y PDF.
- Tests: 47 en Django y 24 en Vue (Vitest), todos en verde. CI en GitHub Actions (`.github/workflows/tests.yml`) con backend y frontend.
- Arnés de IA instalado con DevForge Init (2026-10-03): AGENTS.md, CLAUDE.md y MEMORY.md.

## Decisiones (y por qué)
- AGENTS.md es la fuente única de reglas; CLAUDE.md solo lo importa → mismas reglas para Claude Code y OpenCode.

## Aprendizajes y errores a evitar
- Había un `package.json` con `node_modules` en la raíz (un `npm install` en la carpeta equivocada). Se borró: las dependencias del frontend viven solo en `frontend/`.
- Zona horaria (2026-10-03): con `TIME_ZONE='UTC'` y `date.today()`/`datetime.now()`, la fecha de fin de un medicamento editado salía un día tarde si se creó después de las 19:00, el PDF mostraba horas en UTC y todo dependía del reloj del equipo. Corregido con `TIME_ZONE` configurable y `timezone.localdate()`/`localtime()`.
- La sospecha de recordatorios duplicados o saltados era falsa: el desfase se compensaba solo. Lección: reproducir con un test antes de afirmar un fallo.
- El comando de WhatsApp se caía al escribir 💊 si la salida iba a un archivo cp1252; ahora reemplaza los caracteres que no caben.

## Próximos pasos
- Corregir el README: el venv está en la raíz, no en `backend/venv`.
