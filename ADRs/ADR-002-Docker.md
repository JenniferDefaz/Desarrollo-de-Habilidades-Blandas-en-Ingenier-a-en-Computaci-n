# ADR-002: ¿Por qué Docker + Docker Compose?

**Estado:** Aprobado

**Contexto:** El sistema requiere 5 servicios acoplados (Django, Nginx/React, PostgreSQL 15, Redis 7, MinIO S3).

**Problema:** ¿Cómo asegurar que el entorno de desarrollo sea 100% reproducible y portable entre cualquier equipo o servidor sin errores de configuración?

**Alternativas:** Se evaluaron Instalación Nativa (descartada por inconsistencias "en mi máquina sí funciona") y Máquinas Virtuales Vagrant (descartadas por alto consumo de RAM).

**Decisión:** Contenedorización mediante Docker y orquestación local con Docker Compose (docker compose up --build).

**Consecuencias:** Despliegue automatizado con un solo comando, aislamiento completo de servicios, persistencia de datos mediante volúmenes Docker y preparación directa para PaaS.
