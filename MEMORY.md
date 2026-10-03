# MEMORY.md — MedAlert
Memoria del proyecto entre sesiones. Máximo ~50 líneas: resume o elimina lo que ya no aporte.

## Estado actual
- v1.0 funcionando: cuidadores, pacientes, medicamentos, recordatorios, citas, WhatsApp (CallMeBot) y PDF.
- Tests: 41 en Django y 24 en Vue (Vitest), todos en verde. CI en GitHub Actions (`.github/workflows/tests.yml`) con backend y frontend.
- Arnés de IA instalado con DevForge Init (2026-10-03): AGENTS.md, CLAUDE.md y MEMORY.md.

## Decisiones (y por qué)
- AGENTS.md es la fuente única de reglas; CLAUDE.md solo lo importa → mismas reglas para Claude Code y OpenCode.

## Aprendizajes y errores a evitar
- Había un `package.json` con `node_modules` en la raíz (un `npm install` en la carpeta equivocada). Se borró: las dependencias del frontend viven solo en `frontend/`.

## Próximos pasos
- Revisar la zona horaria del comando `enviar_recordatorios_whatsapp`: compara `ultima_notificacion__date` (fecha en UTC) con `datetime.now().date()` (fecha local). Entre las 19:00 y las 24:00 de Bogotá las dos fechas no coinciden, y un recordatorio podría enviarse dos veces o saltarse. Sin confirmar: primero un test que lo reproduzca.
- Corregir el README: el venv está en la raíz, no en `backend/venv`.
