# ADR-005: ¿Por qué API REST con Django REST Framework?

**Estado:** Aprobado

**Contexto:** La interfaz frontend SPA requiere comunicarse de forma estandarizada con el backend Django.

**Problema:** ¿Qué arquitectura de API utilizar para la exposición de endpoints?

**Alternativas:** Se evaluaron GraphQL (descartado por complejidad en cachés HTTP) y gRPC (descartado por falta de soporte nativo directo en navegador web).

**Decisión:** Exposición de una API RESTful estructurada bajo /api/v1/ utilizando Django REST Framework.

**Consecuencias:** Estándar intuitivo, generación automatizada de documentación Swagger/OpenAPI (Punto 13) y alta mantenibilidad en el equipo.
