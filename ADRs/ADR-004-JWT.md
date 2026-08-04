# ADR-004: ¿Por qué JWT y Autenticación RBAC?

**Estado:** Aprobado

## 1. Contexto y Problema
La plataforma "Sistema Académico / Habilidades Blandas" requiere interactuar de forma segura con una aplicación cliente SPA (Single Page Application, ej. React) desacoplada. Atenderemos al menos a 8 roles de usuarios con niveles de acceso dispares: Autoridades, Docentes, Estudiantes, Administradores del sistema, entre otros.
El problema: **¿Cómo autenticar al usuario y validar su autorización (roles) de manera segura, escalable y sin mantener estado (stateless) en el servidor backend?**

## 2. Alternativas Consideradas
* **Autenticación Basada en Sesiones (Cookies de Sesión Tradicionales):** Descartada. Obliga al servidor a almacenar el ID de sesión en memoria o en una base de datos. Si el sistema escala horizontalmente (múltiples servidores web), se requeriría configurar un servicio de estado distribuido complejo (ej. Session Affinity / Sticky Sessions) para que las sesiones persistan entre peticiones. Además, complica el desarrollo al tener clientes móviles o servicios de terceros.
* **Basic Authentication (HTTP Basic):** Descartada totalmente. Requiere que el cliente envíe las credenciales base64 en cada petición. Sufriría de problemas de seguridad severos si es interceptada, y no soporta revocación nativa ni escalabilidad segura.

## 3. Decisión
Se decide la implementación de **JSON Web Tokens (JWT)** para la autenticación sin estado, combinada con un esquema de control de acceso **RBAC (Role-Based Access Control)** provisto por Django REST Framework y bibliotecas como `djangorestframework-simplejwt`.

## 4. Consecuencias (Justificación y Resultados)
* **Arquitectura Stateless (Sin Estado):** El backend no almacena la sesión en memoria. Toda la información necesaria para identificar al usuario y confirmar su rol está firmada criptográficamente (HMAC / RSA) en el cuerpo del token JWT. Esto permite escalar el backend horizontalmente agregando más contenedores de manera instantánea (RNF01/RNF02).
* **Doble Token (Access / Refresh):** Se emitirá un `Access Token` de vida corta (ej. 15 minutos) para minimizar riesgos de secuestro, y un `Refresh Token` de vida larga (ej. 7 días) almacenado de forma segura en el cliente, logrando un balance óptimo entre seguridad y experiencia de usuario.
* **Control de Autorización Granular (RBAC):** Se crearán Grupos y Permisos a nivel de Django (ej. 'Es_Autoridad', 'Es_Estudiante') integrados en los decoradores de la API, impidiendo que usuarios realicen acciones sobre endpoints a los que no tienen derecho (Previniendo fallas tipo IDOR o Broken Access Control).
