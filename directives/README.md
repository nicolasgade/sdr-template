# directives/ — SOPs y Directivas

Este directorio contiene los Standard Operating Procedures (SOPs) del negocio, escritos en Markdown. Son la **Capa 1** de la arquitectura de 3 capas.

## Qué va aquí

Cada directiva define un proceso de negocio completo:
- **Objetivo** del proceso
- **Entradas** necesarias
- **Herramientas/scripts** a usar (de `execution/`)
- **Salidas** esperadas
- **Casos extremos** y reglas de negocio

## Directivas sugeridas

| Archivo | Propósito |
|---------|-----------|
| `contexto_operativo.md` | Contexto general del negocio: clientes actuales, POP, materiales, reglas permanentes |
| `seguimiento_campana.md` | SOP para seguimiento de campañas por tienda: métricas, clasificación, reportes |
| `facturacion_erp.md` | Proceso de facturación, CFDI, integración con ERP |
| `analisis_rentabilidad_campanas.md` | Framework para evaluar rentabilidad de campañas y dinámicas |

## Cómo crear una directiva nueva

```markdown
# [Nombre del Proceso]

## Objetivo
Qué se logra con este proceso.

## Entradas
- Dato 1
- Dato 2

## Herramientas
- `execution/script.py` — qué hace

## Flujo
1. Paso 1
2. Paso 2
3. Paso 3

## Salidas
- Reporte / archivo / actualización de CRM

## Reglas y casos extremos
- Regla 1
- Si pasa X, hacer Y
```

## Principio clave

Las directivas son documentos vivos. El agente AI las actualiza cuando descubre restricciones, mejores enfoques o errores comunes. Pero NUNCA las sobreescribe sin confirmación del usuario.
