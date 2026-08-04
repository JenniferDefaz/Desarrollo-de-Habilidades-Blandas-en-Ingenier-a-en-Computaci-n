# ADR-001: ¿Por qué PostgreSQL como gestor de BDD?

**Estado:** Aprobado

## 1. Contexto y Problema
El sistema "Plataforma de Habilidades Blandas" (para Ingeniería en Computación) requiere almacenar y gestionar información crítica y estructurada con altos niveles de interrelación. El modelo de datos incluye entidades como usuarios, roles, materias, rúbricas de evaluación dinámicas, encuestas 360° y trazabilidad auditable del progreso de las competencias.
El problema arquitectónico principal radica en: **¿Qué motor de base de datos relacional (o no relacional) nos garantiza transacciones estrictas, alto rendimiento analítico para reportes, y al mismo tiempo soporte para estructuras semi-dinámicas (como las preguntas de evaluación)?**

## 2. Alternativas Consideradas
* **MongoDB (Base de Datos Orientada a Documentos / NoSQL):** Descartado. Si bien aporta muchísima flexibilidad para crear cuestionarios y rúbricas variables, el sistema tiene una naturaleza altamente transaccional. La falta de soporte nativo y eficiente para JOINs y un modelo relacional estricto pondría en riesgo la consistencia de los datos (por ejemplo, al relacionar estudiantes, docentes, periodos académicos y rubros).
* **MySQL / MariaDB:** Descartado. Aunque es ampliamente utilizado y veloz en lecturas, históricamente es menos estricto en chequeos transaccionales por defecto comparado con otras opciones. Además, su manejo de operaciones de indexación y búsqueda sobre campos JSON no es tan maduro o robusto como el de la alternativa ganadora.
* **Bases de datos comerciales (Oracle, SQL Server):** Descartadas por su elevado costo de licenciamiento (vendor lock-in) y porque su adopción no concuerda con un modelo de presupuesto limitado enfocado al sector académico.

## 3. Decisión
Hemos decidido adoptar **PostgreSQL 15 (o superior)** como nuestro Sistema Gestor de Base de Datos principal.

## 4. Consecuencias (Justificación y Resultados)
* **Garantías ACID Sólidas (Cumplimiento de RNF11/RNF12):** PostgreSQL es conocido por su rigidez y fiabilidad, lo que asegura que las notas y registros de evaluación nunca queden en un estado inconsistente en caso de caída del servidor.
* **Tipo de Dato JSONB:** Nos permite almacenar estructuras flexibles (como configuraciones de rúbricas o respuestas a encuestas) dentro del modelo relacional, logrando una arquitectura híbrida que indexa y busca dentro del JSON eficientemente.
* **Integración Perfecta con Django ORM:** El Framework web seleccionado (Django) cuenta con integraciones nativas y exclusivas para PostgreSQL, posibilitando búsquedas full-text, campos de arreglos (`ArrayField`) y restricciones de exclusión.
* **Seguridad y Extensibilidad:** Soporte nativo para esquemas lógicos, gestión de permisos granulares y excelente ecosistema de copias de seguridad continuas (PITR).
