# ADR-003: ¿Por qué PostgreSQL 15?

**Estado:** Aprobado

**Contexto:** Necesidad de almacenar relaciones complejas entre usuarios, evaluaciones 360° y trazabilidad auditable.

**Problema:** ¿Qué motor de base de datos relacional garantiza transacciones estrictas, alto rendimiento en reportes y soporte para estructuras dinámicas?

**Alternativas:** Se evaluaron MongoDB (descartado por falta de transacciones ACID nativas entre colecciones) y MySQL (descartado por menor soporte en tipos JSONB y consultas analíticas).

**Decisión:** Selección de PostgreSQL 15 como motor relacional primario.

**Consecuencias:** Garantías ACID sólidas (RNF11/RNF12), excelente integración nativa con Django ORM, soporte de campos JSONB para rúbricas cambiantes y réplicas de lectura en la nube.
