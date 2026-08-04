# ADR-004: ¿Por qué JWT y Autenticación RBAC?

**Estado:** Aprobado

**Contexto:** La plataforma atiende a 8 roles de usuario distintos en una SPA web desacoplada.

**Problema:** ¿Cómo autenticar y autorizar usuarios de forma segura y sin estado (stateless) en el backend?

**Alternativas:** Se evaluaron Sesiones por Cookie (descartadas por requerir estado en servidor) y HTTP Basic (descartada por inseguridad).

**Decisión:** Implementación de Tokens JWT (Access + Refresh) con djangorestframework-simplejwt y permisos RBAC en Django REST Framework.

**Consecuencias:** Autenticación stateless que facilita el escalado horizontal (RNF01/RNF02), protección de rutas según rol y revocación opcional mediante Redis.
