# ADR-001: ¿Por qué Arquitectura Monolítica Modular (con Django)?

**Estado:** Aprobado

**Contexto:** Caso 4 - Plataforma de Habilidades Blandas (Ingeniería en Computación). El sistema requiere manejar usuarios, competencias, evaluaciones 360°, actividades y reportes altamente interrelacionados.

**Problema:** ¿Qué estilo arquitectónico adoptar para equilibrar modularidad, mantenibilidad, consistencia de datos y bajo costo operacional?

**Alternativas:** Se evaluaron Microservicios Distribuidos (descartados por alta complejidad operacional, latencia de red y consistencia eventual) y Monolito Layered Clásico (descartado por riesgo de acoplamiento).

**Decisión:** Adopción de la Arquitectura Monolítica Modular (Modular Monolith) en Django, delimitando responsabilidades mediante Django Apps independientes (apps.users, apps.evaluations, etc.).

**Consecuencias:** Simplicidad operativa (1 solo contenedor backend), llamadas inter-módulo en memoria de nivel sub-milisegundo (RNF04), transacciones ACID nativas en PostgreSQL y posibilidad de migración futura a microservicios si se requiere.
