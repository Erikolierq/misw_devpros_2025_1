# misw_devpros_2025_1

Esta aplicación es una implementación de microservicios para un laboratorio clínico, diseñada siguiendo los principios de Domain Driven Design (DDD) y una arquitectura basada en eventos. La solución integra varios servicios (usuarios, autenticación, manejo de resultados clínicos, notificaciones y logging) que se comunican entre sí usando el patrón Saga de coreografía y utilizan una base de datos PostgreSQL para la persistencia de datos.

## Requisitos Previos

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Un tester de APIs (por ejemplo, [Postman](https://www.postman.com/))

## Instrucciones de Ejecución

### 1️⃣ Clonar el Repositorio
Clona el repositorio a tu máquina local:

```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_DIRECTORIO>
```

### 2️⃣ Levantar la Aplicación con Docker Compose

Ejecuta el siguiente comando en la raíz del proyecto para construir y levantar todos los microservicios:

```bash
docker-compose up --build
```

#### ¿Qué hace este comando?
- Construirá las imágenes Docker de cada microservicio.
- Levantará el contenedor de PostgreSQL con la persistencia de datos.
- Iniciará todos los microservicios (usuarios, autenticación, item_valor, etc.).

---
📝 **Nota:** Es necesario esperar a que el contenedor create_namespace_topic finalice su ejecución para el correcto funcionamiento de la plataforma, es posible que toque reiniciar los servicios de notification_service y saga_log_service

## 📡 Endpoints y Pruebas con Postman

Utiliza Postman (u otro tester de APIs) para interactuar con los siguientes endpoints:

### 1️⃣ Crear Usuarios

**Método:** `POST`  
**URL:** `http://localhost:8080/users`

#### Body (JSON):
```json
{
  "username": "usuario2",
  "password": "password2",
  "role": 1
}
```

### 2️⃣ Login

**Método:** `POST`  
**URL:** `http://localhost:8080/login`

#### Body (JSON):
```json
{
  "username": "usuario2",
  "password": "password2"
}
```

📝 **Nota:** La respuesta incluirá un token JWT. Para enviar el token en Postman, ve a la pestaña `Authorization`, selecciona `Bearer Token` y pega el token obtenido.

### 3️⃣ Crear un Resultado Clínico

**Método:** `POST`  
**URL:** `http://localhost:8080/results`

#### Body (JSON):
```json
{
  "patient": "Paciente de Prueba",
  "result": "Resultado Positivo"
}
```

🔹 **Nota:** Incluye el token JWT en el header (tipo: Bearer Token).

### 4️⃣ Ver un Resultado Clínico

**Método:** `GET`  
**URL:** `http://localhost:8080/results/1`

#### Headers:
```plaintext
Authorization: Bearer <tu_token_jwt>
```

---

### 5️⃣ Obtener los logs de la aplicación
**Método:** `GET`  
**URL:** `http://localhost:8080/saga/logs`

#### Headers:
```plaintext
Authorization: Bearer <tu_token_jwt>
```


# Semana 6 y 7

## Microservicio `item_valor_service`

### 1. Microservicios basados en eventos
Estamos utilizando Apache Pulsar como broker de eventos, lo que permite la comunicación asincrónica entre servicios mediante eventos.
Se implementó un EventPublisher y un EventConsumer, lo cual es correcto en un enfoque basado en eventos.

### 2. Tipo de evento utilizado
Usa eventos con carga de estado
Los eventos como ResultCreatedEvent y ResultQueriedEvent incluyen datos relacionados con el resultado clínico o el usuario que consulta el resultado.

### 3. Diseño del esquema y su evolución
* Tecnología: Usa PostgreSQL para almacenamiento y Apache Pulsar para mensajería, lo cual es una buena combinación.
* Evolución del esquema: El EventStore permite cierto control sobre la evolución de eventos, pero no hay versión de esquema definida

### 4. Patrón de almacenamiento de datos
Usa almacenamiento descentralizado
Cada servicio tiene su propia base de datos (users_db en PostgreSQL) y no hay dependencias directas a una base de datos centralizada.
¿Por qué?
En un sistema de microservicios, cada servicio maneja su propio almacenamiento para evitar acoplamiento.
El servicio solo interactúa con su propia base de datos (clinical_results).

### 5. Patrón de almacenamiento: CRUD vs Event Sourcing
Usa Event Sourcing
Tenemos un EventStoreRepository que guarda eventos en la base de datos.
ClinicalResultAggregate.rehydrate() reconstruye el estado a partir de eventos pasados.
¿Por qué?
En lugar de almacenar solo el estado actual en la base de datos, se almacenan eventos y pueden reconstruir la historia del agregado (ClinicalResult).
event_store actúa como una fuente de verdad en lugar de una simple tabla con resultados.

### Escenario de calidad aplicado al servicio `item_valor_service`
#### ✔ Escenario 1 (Protección de datos sensibles en el almacenamiento): 
Los datos médicos almacenados estarán cifrados y solo accesibles con credenciales autorizadas.
Se usa la clase `EncryptionService` con la libreria `cryptography` seteando una llave en el environment y así los resultados clínicos son manejados con protección de datos

--- 

## Microservicio `user_service`

### 1. Microservicio basada en eventos: 
El servicio `user_service` sigue los principios de microservicios basados en eventos utilizando Apache Pulsar como broker de mensajes. La comunicación entre servicios se realiza a través de eventos que se publican y consumen de manera asincrónica.

### 2. Tipo de evento utilizado: 
El servicio user_service usa eventos de integración, ya que los eventos publicados (por ejemplo, UserCreatedEvent) notifican a otros microservicios sobre cambios en el estado del usuario, sin contener la carga completa del estado. Estos eventos permiten a otros servicios reaccionar y tomar decisiones sin necesidad de consultar directamente a user_service.
Este enfoque mejora la descentralización y la independencia entre microservicios, alineándose con la arquitectura de eventos.

### 3. Diseño del esquema y su evolución:
* Tecnología: Se usa Apache Pulsar como broker de eventos, con AvroSchema para la serialización de eventos.
* Evolución del esquema: La versión del esquema está definida en schema_version dentro del modelo ResultCreatedSchema. Esto permite manejar cambios evolutivos sin romper compatibilidad con versiones anteriores.
* Beneficio: Al usar Avro con Schema Registry de Pulsar, se facilita la validación de versiones y la compatibilidad con servicios que consumen eventos.

###  4. Almacenamiento de datos: Se usa un modelo híbrido de almacenamiento:
* Base de datos centralizada (PostgreSQL) para mantener la persistencia de usuarios.
* Event Store para almacenar eventos, asegurando que el historial de cambios pueda ser consultado y reproducido si es necesario.
Este enfoque permite un balance entre consistencia y escalabilidad.

###  5. Modelo de almacenamiento: 
Se implementa Event Sourcing, ya que los eventos (UserCreatedEvent, ResultQueriedEvent) se almacenan en el EventStore. Esto permite reconstruir el estado del dominio a partir de la secuencia de eventos.
Justificación:
* Facilita la trazabilidad y auditoría de los cambios.
* Permite la recuperación del estado sin depender de la base de datos relacional.
* Se alinea con DDD al modelar cambios en el dominio mediante eventos de negocio.

###  6. Aplicación de DDD: 
El servicio sigue los principios de Domain-Driven Design (DDD) mediante:
* Agregados: UserAggregate encapsula la lógica de creación de usuarios.
* Contextos acotados: user_service maneja solo la gestión de usuarios.
* Inversión de dependencias: Se usan interfaces como UserRepository y EventStoreRepository para desacoplar la infraestructura del dominio.

Capas y arquitectura cebolla:
* domain/ para la lógica de dominio.
* application/ para manejadores de comandos y eventos.
* infrastructure/ para acceso a datos, encriptación y comunicación con Pulsar.
Esto garantiza un diseño modular, flexible y alineado con las mejores prácticas de microservicios basados en eventos.

### Escenario de calidad aplicado al servicio `user_service`
#### ✔ Escenario #5 (Alta disponibilidad del API en caso de alta demanda): 
Para evitar que un solo usuario sobrecargue el sistema, aplicamos Rate Limiting.
Se limita el consumo de las APIs por usuario, se establece en el archivo `app.py` con la libreria `flask-limiter` seteando un cantidad de llamados para POST, GET y en general.

## Microservicio notifications_service

### 1. Microservicios basados en eventos
El servicio de notificaciones sigue un enfoque basado en eventos, donde reacciona a eventos publicados en Apache Pulsar y ejecuta acciones en respuesta a estos eventos.

Event Consumer: Escucha eventos desde event-user y event-topic para enviar notificaciones por correo.
Event Publisher: Puede enviar eventos de confirmación de envío de notificación.

### 2. Tipo de evento utilizado
El notifications_service procesa eventos de tipo "evento con carga de estado".
Acción: Notificar al paciente sobre el resultado médico.

### 3. Diseño del esquema y su evolución
Tecnología:
Base de datos PostgreSQL para almacenamiento de logs de notificaciones.
Apache Pulsar como sistema de mensajería de eventos.
Evolución del esquema:
Se usa JSON en los eventos, permitiendo flexibilidad para añadir nuevos campos sin romper la compatibilidad.
Se podría mejorar con Avro Schema Registry para validar cambios de esquema.

### 4. Patrón de almacenamiento de datos
✅ Usa almacenamiento descentralizado
Cada servicio maneja su propia base de datos de manera independiente.

notifications_service almacena logs de notificaciones, pero no mantiene datos persistentes de usuarios o resultados clínicos.
Solo interactúa con eventos entrantes y no consulta bases de datos de otros servicios.
🔹 ¿Por qué este diseño?

Evita acoplamiento entre microservicios.
Facilita la escalabilidad, permitiendo que el servicio de notificaciones opere de manera autónoma.

### 5. Patrón de almacenamiento: CRUD vs Event Sourcing
✅ Usa almacenamiento basado en eventos
No maneja registros directos de usuarios o resultados, sino que reacciona a eventos y registra logs de notificaciones enviadas.
Event Sourcing ayuda a reconstruir el historial de notificaciones para auditoría.

### 6. Uso de Saga con el Patrón de Coreografía
El notifications_service participa en una Saga con coreografía, ya que no depende de un orquestador central, sino que reacciona automáticamente a eventos.

🔹 Cómo funciona la coreografía en este servicio:
El users_service publica el evento UserCreatedEvent.
El notifications_service escucha este evento y envía un correo de bienvenida.
El saga_log_service registra el evento en la base de datos para auditoría.
En este modelo, cada servicio reacciona a los eventos de manera independiente, sin necesidad de coordinación manual.

### 7. Uso del patrón BFF (Backend for Frontend)
El servicio de notificaciones es consumido indirectamente a través del API Gateway (BFF).

📌 Los clientes front-end no interactúan directamente con notifications_service, sino que hacen peticiones al BFF.
📌 Beneficios de este enfoque:
Menos carga en el front-end: No necesita manejar lógica de autenticación ni interactuar con múltiples microservicios.
Optimización de peticiones: Un solo request al BFF puede consolidar respuestas de varios servicios.

## Microservicio saga_log_service

### 1. Microservicios basados en eventos
El saga_log_service sigue un modelo de event-driven architecture, registrando eventos en una base de datos PostgreSQL.

Escucha eventos desde Apache Pulsar en event-user y event-topic.
Registra estos eventos para auditoría y depuración.

### 2. Tipo de evento utilizado
Eventos con carga de estado, donde cada evento contiene datos relevantes sobre la operación ejecutada.

### 3. Diseño del esquema y su evolución
Base de datos: PostgreSQL (saga_log_db) con la tabla saga_log.
Formato flexible: Almacena eventos en formato JSON, permitiendo compatibilidad con futuros cambios.

### 4. Patrón de almacenamiento de datos
✅ Usa almacenamiento descentralizado
Cada microservicio maneja su propia base de datos.

saga_log_service solo registra eventos, sin modificar datos en otros servicios.
No depende directamente de la base de datos de users_service o item_valor_service.

### 5. Patrón de almacenamiento: CRUD vs Event Sourcing
✅ Usa Event Sourcing
saga_log_service actúa como un almacén de eventos, guardando el historial de cada transacción de la saga.
Beneficio: Se puede reconstruir la secuencia completa de eventos en caso de fallas o auditorías.

### 6. Implementación de Saga con Coreografía
saga_log_service no controla la lógica de la Saga, sino que simplemente registra eventos.
Ventaja: No introduce dependencias innecesarias en la lógica del negocio.
📌 Ejemplo de flujo Saga Coreografía:

users_service crea un usuario y publica UserCreatedEvent.
notifications_service escucha el evento y envía un correo.
saga_log_service registra ambos eventos (UserCreated y NotificationSent).
Si hay errores, saga_log_service guarda el estado como "FAILED" para recuperación manual o reintento.

### 7. Monitoreo y observabilidad de la Saga
Consulta de eventos en /saga/logs:
Permite obtener un historial detallado de eventos procesados.
Estados de eventos:
"RECEIVED": Evento recibido pero no procesado aún.
"PROCESSED": Evento almacenado correctamente.
"FAILED": Hubo un error al procesar el evento.
