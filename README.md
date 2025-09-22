# Articles sistema FastAPI



## Estructura del proyecto o arbol del proyecto 
``` 
articulos/
├── app/
│   ├── api/          # Endpoints FastAPI y dependencias comunes
│   ├── cache.py      # Wrapper Redis (ArticleCache)
│   ├── config.py     # Configuración centralizada (env vars)
│   ├── crud/         # Repositorios SQLAlchemy
│   ├── database.py   # Engine, sesión y declarative base
│   ├── main.py       # Instancia FastAPI + /health
│   ├── models/       # Modelo ORM Article
│   ├── schemas/      # Esquemas Pydantic
│   └── services/     # Lógica de negocio + caché
├── alembic/          # Migraciones Alembic
├── docs/postman/     # Colección Postman para probar endpoints
├── tests/            # Pytest (CRUD, servicios, API, integración)
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Requisitos previos
Instala estas herramientas en tu máquina antes de comenzar:
 
| Herramienta |.                     |Versión recomendada|              | Cómo comprobar |
| ----------- |                      -------------------                 | -------------- |
| Docker Desktop / Docker Engine     | ≥ 20.10 |                         |`docker --version` |
| Docker Compose (plugin incluido).  | ≥ 2.10                            | `docker compose version` |
| curl |                             |Cualquier versión reciente  |      | `curl --version` |
| Python                             | ≥ 3.11                            | `python3 --version` |
| Postman o Insomnia                 | Última versión                    | `redis-server --version`|
|Redis                                

> Docker es indispensable porque toda la solución (API + PostgreSQL + Redis) corre dentro de contenedores.

### Imágenes Docker utilizadas
| Servicio    |        Imagen          | Versión |
| --------    | ------     -------     -----------
| API         | `python:3.11-slim`     | 3.11.x |
| PostgreSQL  | `postgres:15-alpine`   | 15.x   |
| Redis       | `redis:7-alpine`       | 7.x    |

### Dependencias Python instaladas (se cargan dentro del contenedor `api` las dependencias se encuentran en el archivo requeriments.txt)
| Paquete | Versiones declaradas                 | ¿Para qué se usa? |
| ------- | --------------------                 | ----------------- |
| `alembic>=1.13.1,<2.0.0`                       | Manejo de migraciones de la base de datos PostgreSQL. |
| `fastapi>=0.111.0,<0.112.0`.                   | Framework web para definir los endpoints REST. |
| `uvicorn[standard]>=0.30.0,<0.31.0`            | Servidor ASGI que ejecuta la aplicación FastAPI. |
| `sqlalchemy>=2.0.29,<2.1.0`                    | ORM y construcción de consultas SQL. |
| `psycopg[binary]>=3.1.18,<3.2.0`               | Driver PostgreSQL utilizado por SQLAlchemy. |
| `redis>=5.0.3,<6.0.0`                          | Cliente para interactuar con Redis y gestionar la caché. |
| `pydantic>=2.7.1,<3.0.0`                       | Validación y serialización de datos (schemas del API). |
| `pydantic-settings>=2.2.1,<3.0.0`              | Carga tipada de variables de entorno para la configuración. |
| `python-dotenv>=1.0.1,<2.0.0`                  | Lectura del archivo `.env` en entornos locales. |
| `pytest>=8.2.0,<9.0.0`                         | Framework de pruebas unitarias e integración. |
| `httpx>=0.27.0,<0.28.0`                        | Cliente HTTP utilizado en pruebas para consumir la API. |



## 0. Primeros pasos
1. Clona el repositorio (o descarga el código) y abre una terminal dentro de la carpeta raíz.
2. En este repositorio el código vive dentro del directorio `articulos/`, así que cada vez que se indique un comando, asume que debes ejecutarlo desde ahí:
   para acceder a la carpeta solo escribe en terminal 
   ```
   cd articulos  
   ```
     si te encuentras en otra carpeta por ejemplo gestion y la del programa articulos todo lo que se ejecutara se debe ejecutar en terminal de la repo  por ejemplo "cd articulos" en mi caso esto te guia a la carpeta de la repo a la cual realizaras las operaciones 



### 1. Copiar variables de entorno
Con la terminal ubicada dentro de `articulos/`, ejecuta:
``` 
cp .env.example .env
```
Ajusta valores si lo necesitas (por ejemplo `API_KEY` o credenciales de base de datos). El archivo `.env` será leído por la API y por Alembic.


### 2. Levantar los contenedores
En la misma terminal del proyecto ejecuta:
```
docker compose up --build
```
Este comando construye la imagen de la API y arranca los contenedores `articles-api`, `articles-db` (PostgreSQL) y `articles-redis`. Déjalo corriendo en la terminal si la cierras, el entorno se apaga.


### 3. Aplicar migraciones a la base principal
Abre otra terminal, vuelve a entrar a `articulos/` y corre:
``` 
docker compose exec api sh -lc "PYTHONPATH=/app alembic upgrade head"
```
Esto crea la tabla `articles` con sus restricciones e índices. De lo contrario los `POST /articles` devolverán error 500.


### 4. Crear la base de datos de pruebas
En cualquiera de las terminales ubicadas en `articulos/`, crea la base solo una vez:
``` 
docker compose exec db psql -U postgres -c "CREATE DATABASE articles_test;"
``` 
Si ya existía, PostgreSQL mostrará un aviso y continuará.


### 5. Ejecutar las pruebas automatizadas
Aún dentro de `articulos/`, lanza las pruebas con:
```
docker compose exec api pytest
```
Deberías ver `14 passed` (es normal recibir algunos warnings sobre futuras deprecaciones). Esto confirma que repositorio, servicios, caché y endpoints funcionan.



###  Probar manualmente el CRUD con `curl` desde la terminal dentro de la carpeta articulos 
Mantén abierta la terminal donde corre `docker compose up`; todos los comandos dependen de que API, PostgreSQL y Redis sigan activos.


1. **Crear prueba health de manera manual**
Para probar el endpoint de health manualmente, basta con una llamada Get simple.
 - Ejecuta en la terminal situada en `articulos/`:
 ```
   curl http://localhost:8000/health

 ```
 - Resultado esperado {"status":"ok"} 
 - Eso confirma que la aplicación FastAPI está levantada y atendiendo peticiones.


2. **Crear artículo (POST)**
Envía un JSON a `POST /articles/` con título, cuerpo, etiquetas y autor. El header `x-api-key` es obligatorio.
   - Ejecuta en la terminal situada en `articulos/`:
     ``` 
     curl -i -H "Content-Type: application/json" -H "x-api-key: local-dev-key" -d '{"title":"Articulo CLI 002","body":"Contenido inicial","tags":["fastapi"],"author":"Ana"}' http://localhost:8000/articles/
     ```
   - Resultado esperado: `HTTP/1.1 201 Created` con el artículo y su `id`. Anota ese `id`; lo usarás más adelante.


3. **Listar artículos (GET)**
   - Consulta `GET /articles/` aplicando filtros de paginación (`limit`, `author`). El artículo creado en el paso 1 debe aparecer en `items`.
   - Ejecuta en la terminal situada en `articulos/`:
     ```
     curl -i -H "x-api-key: local-dev-key" "http://localhost:8000/articles/?limit=5&author=Ana"
     ```
   - Resultado esperado: `HTTP/1.1 200 OK` con un JSON que incluye `items`, `total`, `limit` y `skip`.


4. **Obtener por ID (GET)**
   - Recupera un artículo específico usando el `id` obtenido en el paso 1. Si el dato está en Redis, responde desde la caché; si no, va a PostgreSQL y la actualiza.
   - Sustituye `<ID_OBTENIDO>` con tu ID real (sin `<` ni `>`). Ese `id` es el mismo que obtuviste en el paso 1:
   - Ejecuta en la terminal situada en `articulos/`:
     ```
     curl -i -H "x-api-key: local-dev-key" http://localhost:8000/articles/<ID_OBTENIDO>   
     ```
   - Resultado esperado: `HTTP/1.1 200 OK` con el JSON del artículo.


5. **Actualizar (PUT)**
   - Cambia campos puntuales (`body`, `tags`, etc.). Tras actualizar en PostgreSQL, el servicio refresca la caché con los nuevos valores.
   - Usa el mismo `id`:
   - Ejecuta en la terminal situada en `articulos/`:
     ```
     curl -i -X PUT -H "Content-Type: application/json" -H "x-api-key: local-dev-key" -d '{"body":"Contenido actualizado","tags":["fastapi","v2"]}' http://localhost:8000/articles/<ID_OBTENIDO>
     ```
   - Resultado esperado: `HTTP/1.1 200 OK` y el artículo con los nuevos valores (`body`, `tags`, `updated_at`).


6. **Eliminar (DELETE)**
   - Borra el artículo en PostgreSQL y elimina la clave `article:{id}` en Redis.
   - Ejecuta en la terminal situada en `articulos/`:
     ```
     curl -i -X DELETE -H "x-api-key: local-dev-key" http://localhost:8000/articles/<ID_OBTENIDO>
     ```
   - Resultado esperado: `HTTP/1.1 204 No Content` (sin cuerpo).


7. **Confirmar eliminación (opcional)**
   - Repite el paso 3. Ahora deberías recibir `HTTP/1.1 404 Not Found` con `{"detail":"Artículo no encontrado"}`.


## Resumen de pruebas manuales del CRUD
1. **Crear artículo** – `POST /articles/` con JSON (title, body, tags, author) y header `x-api-key`. Respuesta esperada: `201 Created` con el artículo y su `id`.
2. **Listar artículos** – `GET /articles/?limit=5&author=Ana`. Respuesta esperada: `200 OK` con `items`, `total`, `limit`, `skip`.
3. **Consultar por ID** – `GET /articles/{id}`. Usa caché si está disponible. Respuesta esperada: `200 OK` con el artículo.
4. **Actualizar** – `PUT /articles/{id}` con los campos a modificar. Respuesta esperada: `200 OK` con el artículo actualizado.
5. **Eliminar** – `DELETE /articles/{id}`. Respuesta esperada: `204 No Content` y eliminación en DB + caché.
6. **Confirmar eliminación (opcional)** – `GET /articles/{id}` nuevamente. Respuesta esperada: `404 Not Found`.




### Probar con Postman o Insomnia (opcional)
A continuación tienes el paso a paso para usar la colección incluida.
se tiene que buscar el archivo directamente en la carpeta de articulos y buscas dentro de la carpeta el archivo 
1. Importa `docs/postman/ArticlesManagement.postman_collection.json`.
2. Ajusta las variables `base_url` (normalmente `http://localhost:8000`) y `api_key` (la misma clave que pusiste en `.env`). Deja `article_id` vacío al inicio y pulsa **Save**.
3. Ejecuta las peticiones en orden (Health → Create → Get → List → Update → Delete). Cuando hagas **Create Article**, toma el `id` de la respuesta, vuelve a la pestaña de variables, pégalo en `article_id` y guarda para poder usarlo en Get/Update/Delete.



## Endpoints principales
| Método | Ruta              | Descripción                                                                         | Header `x-api-key` |
| ------ | ----------------- | ----------------------------------------------------------------------------------- | ------------------ |
| GET    | `/health`         | Health check sencillo                                                               | si                 |
| POST   | `/articles/`      | Crea un artículo; valida (title, author) únicos y cachea el resultado               | Sí                 |
| GET    | `/articles/`      | Lista artículos con paginación, filtros por autor/tag y orden por `published_at`    | Sí                 |
| GET    | `/articles/{id}`  | Recupera un artículo; consulta primero la caché Redis                               | Sí                 |
| PUT    | `/articles/{id}`  | Actualiza campos opcionales y refresca la caché                                     | Sí                 |
| DELETE | `/articles/{id}`  | Elimina un artículo e invalida la caché                                             | Sí                 |

La caché usa claves `article:{id}` con TTL de 120 s.

---

## Variables de entorno más importantes
- `API_KEY`: clave que debe enviarse en el header `x-api-key`.
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: configuración de la base principal.
- `REDIS_URL`: URL de Redis (ejemplo `redis://redis:6379/0`).
- `DATABASE_URL`: DSN que usa Alembic/SQLAlchemy (si no se define, se construye con los valores anteriores).

---

## Errores comunes y soluciones rápidas
| Mensaje | Explicación | Cómo resolver |
| ------- | ----------- | ------------- |
| `{"detail":"API key inválido"}` | Falta el header `x-api-key` o el valor no coincide | Usa `-H "x-api-key: <tu_clave>"` en todas las peticiones |
| `500 Internal Server Error` al crear | Falta aplicar migraciones (tabla `articles` inexistente) | Repite `docker compose exec api sh -lc "PYTHONPATH=/app alembic upgrade head"` |
| `database "articles_test" does not exist` | No se creó la base usada por pytest | Ejecuta `docker compose exec db psql -U postgres -c "CREATE DATABASE articles_test;"` |
| `psycopg.OperationalError` | PostgreSQL no está listo o el contenedor está detenido | Verifica `docker compose ps` y reinicia si es necesario |
| `curl: (6) Could not resolve host: ...` | Se dejó `...` literal en el comando | Elimina los puntos suspensivos, usa la URL real |
| `HTTP/1.1 307 Temporary Redirect` | Llamaste `/articles` sin la barra final | Usa `/articles/` o agrega `-L` para seguir la redirección |

Para más detalles revisa los logs:
```
docker compose logs -f api
```


## Apagar y limpiar el entorno
1. En la terminal donde corre `docker compose up`, presiona `Ctrl+C`.
2. Opcional: elimina contenedores, red y volúmenes (borra datos de Postgres/Redis) con:
   ```
 docker compose down -v

   ```

¡Listo Finalizamos la prueba hasta aqui!





