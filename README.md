# misw_devpros_2025_1

Esta aplicación es una implementación de microservicios para un laboratorio clínico, diseñada siguiendo los principios de Domain Driven Design (DDD) y una arquitectura basada en eventos. La solución integra varios servicios (usuarios, autenticación, y manejo de resultados clínicos) que se comunican entre sí y utilizan una base de datos PostgreSQL para la persistencia de datos.

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

## 📡 Endpoints y Pruebas con Postman

Utiliza Postman (u otro tester de APIs) para interactuar con los siguientes endpoints:

### 1️⃣ Crear Usuarios

**Método:** `POST`  
**URL:** `http://localhost:8080/users/users`

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
**URL:** `http://localhost:8080/auth/login`

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
**URL:** `http://localhost:8080/item_valor/results`

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
**URL:** `http://localhost:8080/item_valor/results/1`

#### Headers:
```plaintext
Authorization: Bearer <tu_token_jwt>
```
📌 Este endpoint recupera el resultado clínico solo para usuarios autenticados con rol 2.

---

## 🛠 Explicación de la Implementación

Se implementó uno de los servicios de la arquitectura (el servicio **Item Valor**) siguiendo estos principios:

### 📌 Domain Driven Design (DDD)

Se definió el dominio del servicio mediante la entidad `ClinicalResult` y se establecieron eventos de dominio como `ResultCreatedEvent` y `ResultQueriedEvent`.

### 📌 Arquitectura Hexagonal

La solución se organiza en capas:

- **Dominio**: Lógica central del negocio.
- **Infraestructura**: Persistencia con `SQLAlchemy` y `PostgreSQL`.
- **Aplicación**: Exposición de API con `Flask`.


### 📌 Patrón CQS (Command Query Separation)

Se separan claramente:

- **Operaciones de comando** (creación de resultados clínicos).
- **Operaciones de consulta** (lectura de resultados clínicos).

## Microservicio item_valor_service

### Arquitectura de `item_valor_service`


### 1. Microservicios basados en eventos
Estamos utilizando Apache Pulsar como broker de eventos, lo que permite la comunicación asincrónica entre servicios mediante eventos.
Se implementó un EventPublisher y un EventConsumer, lo cual es correcto en un enfoque basado en eventos.


### 2. Tipo de evento utilizado
✅ Usa eventos con carga de estado
Los eventos como ResultCreatedEvent y ResultQueriedEvent incluyen datos relacionados con el resultado clínico o el usuario que consulta el resultado.

### 3. Diseño del esquema y su evolución
Tecnología: Usa PostgreSQL para almacenamiento y Apache Pulsar para mensajería, lo cual es una buena combinación.
Evolución del esquema: El EventStore permite cierto control sobre la evolución de eventos, pero no hay versión de esquema definida

### 4. Patrón de almacenamiento de datos
✅ Usa almacenamiento descentralizado
Cada servicio tiene su propia base de datos (users_db en PostgreSQL) y no hay dependencias directas a una base de datos centralizada.
¿Por qué?
En un sistema de microservicios, cada servicio maneja su propio almacenamiento para evitar acoplamiento.
Tu servicio solo interactúa con su propia base de datos (clinical_results), lo cual es correcto.

### 5. Patrón de almacenamiento: CRUD vs Event Sourcing
✅ Usa Event Sourcing
Tienes un EventStoreRepository que guarda eventos en la base de datos.
ClinicalResultAggregate.rehydrate() reconstruye el estado a partir de eventos pasados.
¿Por qué?
En lugar de almacenar solo el estado actual en la base de datos, almacenas eventos y puedes reconstruir la historia del agregado (ClinicalResult).
event_store actúa como una fuente de verdad en lugar de una simple tabla con resultados.

