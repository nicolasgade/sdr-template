# execution/ — Scripts de Ejecución

Scripts de Python deterministas que el agente AI orquesta. Cada script maneja una tarea específica y se ejecuta vía CLI o importación Python.

## Scripts incluidos

| Script | Propósito |
|--------|-----------|
| `gmail_client.py` | Gmail API: buscar emails, crear/eliminar borradores, leer mensajes |
| `fix_drafts_signature.py` | Actualizar borradores masivamente con firma HTML |
| `analyze_campaign_profitability.py` | Calcular rentabilidad de campañas (ROI, break-even, márgenes) |

## Setup

### 1. Instalar dependencias

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 2. Configurar Gmail OAuth2

1. Crear proyecto en [Google Cloud Console](https://console.cloud.google.com/)
2. Habilitar la Gmail API
3. Crear credenciales OAuth2 tipo "Desktop App"
4. Descargar `credentials.json` a la raíz del proyecto
5. Ejecutar autenticación:

```bash
python3 execution/gmail_client.py auth
```

6. Completar el flujo OAuth en el navegador
7. Se creará `token.json` automáticamente

### 3. Configurar firma HTML

Editar `fix_drafts_signature.py`:
- Reemplazar `SIGNATURE_HTML` con tu firma real
- Personalizar `TEMPLATE` con tu producto
- Configurar `CHANNEL_REFS` con tus canales

### 4. Configurar análisis de rentabilidad

Editar `analyze_campaign_profitability.py`:
- Llenar `SKU_DEFAULTS` con costos unitarios reales
- Llenar `CLIENT_PRICES` con precios por cliente

## Agregar nuevos scripts

Cuando necesites automatizar una tarea nueva:
1. Crear el script en `execution/`
2. Documentar uso CLI en el docstring
3. Actualizar la directiva correspondiente en `directives/`
4. El agente AI usará el script automáticamente
