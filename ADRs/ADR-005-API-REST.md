# ADR-005: ¿Por qué API REST con Django REST Framework?

**Estado:** Aprobado

## 1. Contexto y Problema
Para proporcionar una interfaz de usuario rica, moderna y reactiva, se ha decidido que el Frontend (SPA) sea un componente totalmente separado de la lógica de datos. Esta separación implica que el sistema Frontend necesita un mecanismo estandarizado para consultar, crear, modificar y eliminar datos del sistema (Evaluaciones, Rúbricas, Usuarios).
El problema: **¿Bajo qué protocolo y arquitectura de comunicación de red se deben exponer los datos del servidor (Django) hacia los clientes consumidores?**

## 2. Alternativas Consideradas
* **GraphQL:** Descartado para la fase inicial. Aunque permite a los clientes solicitar exactamente los datos que necesitan (reduciendo over-fetching), añade una curva de aprendizaje pronunciada al equipo, y complica drásticamente factores operacionales críticos como el almacenamiento en caché HTTP estandarizado, el manejo de errores y las consultas recursivas (N+1 queries risk en la base de datos).
* **gRPC / Protocol Buffers:** Descartado. Muy eficiente para comunicación de microservicios backend-to-backend debido a sus payloads binarios, pero no cuenta con soporte nativo amigable en los navegadores web modernos sin requerir proxys intermedios pesados (gRPC-Web).
* **Renderizado de Plantillas (Django Views clásicas):** Descartado. Limitaría severamente las interacciones dinámicas en la UI y acoplaría la presentación con la lógica de base de datos.

## 3. Decisión
Adoptar la arquitectura **API RESTful (Representational State Transfer)**, expondida mediante la biblioteca oficial de **Django REST Framework (DRF)**.

## 4. Consecuencias (Justificación y Resultados)
* **Estándar de la Industria e Interoperabilidad:** REST utiliza los verbos HTTP universales (GET, POST, PUT, PATCH, DELETE) y códigos de estado semánticos (200, 201, 400, 403, 404), facilitando la integración futura con cualquier otra plataforma (Móvil Android/iOS o integraciones con servicios Universitarios).
* **Serialización Avanzada:** DRF facilita la conversión de modelos complejos de base de datos directamente a JSON, resolviendo eficientemente las relaciones de llaves foráneas.
* **Documentación Automatizada:** Al seguir convenciones REST y utilizar DRF, habilitamos la generación automática de la especificación técnica mediante Swagger / OpenAPI 3.0, lo cual es un requisito crucial para la mantenibilidad y presentación de este proyecto académico (Sección de Documentación).
* **Control de Tasas y Paginado Integrado:** DRF incorpora soluciones listas para la producción para paginar grandes resultados (ej. lista de todos los estudiantes) y limitar las peticiones por segundo (Throttling) protegiendo el sistema de abusos.
