# SDR Agent — Plantilla

Plantilla de un **agente de IA para prospección de ventas (SDR)** que armé para mi operación comercial y que funciona dentro de [Cursor](https://cursor.com).

La idea es simple: el agente investiga prospectos, encuentra correos verificados, redacta borradores de email personalizados y deja todo registrado en un CRM. Tú solo entras, revisas y envías.

> Es una base muy sencilla. No es magia ni nada del otro mundo. Es algo que me ha funcionado a mí y que cualquiera puede tomar y mejorar con sus propias herramientas.

## Arquitectura de 3 capas

La gracia está en separar responsabilidades para que sea confiable:

1. **Directivas (`directives/`)** — qué hacer. SOPs en Markdown: objetivos, entradas, herramientas, salidas y reglas de cada proceso.
2. **Orquestación (el agente)** — toma de decisiones. Lee las directivas, llama los scripts en el orden correcto, maneja errores y pide aclaraciones.
3. **Ejecución (`execution/`)** — hacer el trabajo. Scripts de Python deterministas que llaman APIs, procesan datos y hablan con el CRM.

Las **reglas (`.cursor/rules/`)** cargan automáticamente el contexto correcto en cada chat (email copy, cadencia de follow-up, CRM, Gmail, investigación de prospectos).

## Qué incluye

```
.
├── .cursor/rules/        # Reglas que cargan contexto automáticamente en Cursor
├── directives/           # SOPs / procesos de negocio en Markdown
├── execution/            # Scripts de Python (Gmail, firma, rentabilidad)
├── .env.example          # Variables de entorno (copiar a .env)
├── AGENTS.md / CLAUDE.md # Instrucciones maestras del agente
└── README.md
```

## Herramientas que conecta

- **Apollo.io** — enrichment de contactos y correos verificados.
- **Apify** — scraping de Google Maps / web cuando no hay datos en Apollo.
- **Gmail API** — crea borradores de email (nunca envía solo).
- **CRM** — registra clientes, actividades y tareas de seguimiento.

## Quickstart

1. Clona el repo y ábrelo en Cursor.
2. Copia `.env.example` a `.env` y llena tus propias claves.

```bash
cp .env.example .env
```

3. Instala las dependencias de Python:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib requests
```

4. Configura Gmail OAuth2 (ver `execution/README.md`).
5. Personaliza `AGENTS.md` / `CLAUDE.md` con tu producto, clientes y reglas de negocio.
6. Empieza a pedirle tareas al agente dentro de Cursor.

## Importante

- Esta plantilla **no incluye ninguna clave**. Todos los valores sensibles son placeholders (`your_api_key_here`, `[TU_API_KEY]`). Pon las tuyas en `.env`.
- `token.json` y `credentials.json` están en `.gitignore`. Nunca los subas.
- Adapta las directivas y reglas a tu propio negocio: el copy, los precios y las reglas que vienen aquí son ejemplos.

## Licencia

Úsalo libremente y mejóralo. Si te sirve, comparte.
