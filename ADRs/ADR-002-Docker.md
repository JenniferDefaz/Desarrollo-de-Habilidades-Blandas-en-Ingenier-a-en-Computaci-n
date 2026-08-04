# ADR-002: ¿Por qué Docker + Docker Compose?

**Estado:** Aprobado

## 1. Contexto y Problema
El desarrollo de la "Plataforma de Habilidades Blandas" involucra a múltiples componentes interactuando entre sí. El ecosistema planificado contempla al menos los siguientes servicios:
1. Backend (Django REST Framework).
2. Frontend SPA (React / Vue o similar) servido mediante un servidor web como Nginx.
3. Base de Datos Relacional (PostgreSQL 15).
4. (Opcional a futuro) Sistemas de Caché/Workers (Redis) y Almacenamiento de Objetos (MinIO).

El problema principal: **¿Cómo asegurar que el entorno de desarrollo sea 100% reproducible y portable entre cualquier equipo (ya sea Windows, macOS o Linux) de los desarrolladores o los servidores de producción, evitando los clásicos errores de "en mi máquina sí funciona"?**

## 2. Alternativas Consideradas
* **Instalación Nativa (Bare Metal):** Descartada. Requeriría que cada desarrollador o administrador de sistemas instale y configure a mano Python, Node.js, PostgreSQL y Nginx, lidiando con incompatibilidades de versiones del sistema operativo, colisión de puertos y variables de entorno ocultas.
* **Máquinas Virtuales Tradicionales (VMware, VirtualBox, Vagrant):** Descartadas. Aunque logran la aislación deseada, consumen demasiados recursos (RAM, CPU, Disco) al requerir la virtualización de un Sistema Operativo invitado (Guest OS) completo para cada servicio, ralentizando el entorno de desarrollo local y encareciendo el despliegue.

## 3. Decisión
Hemos decidido **contenedorizar todos los servicios de la aplicación utilizando Docker**, y orquestarlos en entornos locales y de pruebas tempranas **utilizando Docker Compose**.

## 4. Consecuencias (Justificación y Resultados)
* **Reproducibilidad Absoluta:** Un archivo `Dockerfile` define explícitamente el sistema operativo base, dependencias (ej. `python:3.12-slim`), y pasos de instalación. Todos ejecutan exactamente el mismo binario del proyecto.
* **Onboarding Inmediato de Desarrolladores:** Un nuevo programador solo necesita instalar Docker y ejecutar `docker-compose up --build`. No es necesario configurar bases de datos manuales ni crear usuarios de BD; todo está automatizado.
* **Aislamiento e Infraestructura como Código (IaC):** La red de servicios está encapsulada. El archivo `docker-compose.yml` sirve además como documentación viva de la arquitectura de la infraestructura.
* **Preparación para Producción y Cloud:** Al tener imágenes de contenedores listas, migrar el sistema hacia plataformas en la nube (PaaS) que soporten orquestadores mayores (Kubernetes, AWS ECS, Google Cloud Run) es un proceso directo y trivial.
* **Manejo de Persistencia:** Los volúmenes Docker (ej. `postgres_data`) aseguran que la base de datos no se pierda al reiniciar o destruir contenedores locales, simulando un disco de red.
