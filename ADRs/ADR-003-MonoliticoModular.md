# ADR-003: ¿Por qué Arquitectura Monolítica Modular (con Django)?

**Estado:** Aprobado

## 1. Contexto y Problema
El sistema está diseñado para evaluar habilidades blandas en la carrera de Ingeniería en Computación. Requiere gestionar módulos de: Usuarios (estudiantes/profesores/autoridades), Evaluaciones 360°, Reportes, Competencias, y Actividades académicas.
El problema arquitectónico: **¿Qué estilo estructural se debe adoptar para que la base de código mantenga un equilibrio adecuado entre mantenibilidad a largo plazo, consistencia de la información y un bajo costo operacional/cognitivo para el equipo de desarrollo actual?**

## 2. Alternativas Consideradas
* **Microservicios Distribuidos:** Descartados. Separar el sistema en 5 APIs independientes implicaría un alto acoplamiento en red. Dado que la evaluación 360° necesita consultar datos tanto del módulo de usuarios como del módulo de actividades, se generaría latencia de red innecesaria (Llamadas HTTP inter-servicio), requeriría orquestación compleja (Sagas, RabbitMQ) y manejo de "Consistencia Eventual". El equipo no tiene actualmente la escala organizativa para mantener infraestructuras distribuidas de tan alta complejidad.
* **Monolito de Capas Clásico (Spaghetti Code):** Descartado. Dejar todos los modelos, controladores y vistas en una sola estructura sin límites de contexto (Bounded Contexts) genera un riesgo enorme de acoplamiento, volviendo frágil la aplicación ante cualquier cambio mínimo (ej. tocar un reporte rompe la autenticación).

## 3. Decisión
Adopción de una **Arquitectura Monolítica Modular (Modular Monolith)**, estructurada nativamente alrededor del paradigma de Aplicaciones (Apps) independientes que ofrece el framework Django.

## 4. Consecuencias (Justificación y Resultados)
* **Simplicidad Operativa:** El sistema completo se despliega en 1 solo contenedor de backend y se escala replicando ese mismo contenedor, lo que abarata significativamente el costo de alojamiento (Hosting).
* **Comunicación en Memoria:** Los distintos módulos interactúan a través de importaciones limpias en código Python, operando a tiempos sub-milisegundo en la misma CPU y compartiendo la misma transacción ACID en la base de datos, lo que garantiza el Rendimiento (RNF04) y la Fiabilidad (RNF11).
* **Delimitación de Responsabilidades:** En Django, dividimos el código en `apps.users`, `apps.evaluations`, `apps.reports`, etc. Cada módulo tiene sus propias migraciones, modelos y pruebas aisladas, facilitando la mantenibilidad a largo plazo.
* **Transición Futura Posible:** Si el sistema crece exponencialmente y un módulo (ej. Reportes) genera demasiada carga, el desacoplamiento lógico interno facilita su extracción a un microservicio real en el futuro, sin tener que reescribir todo desde cero.
