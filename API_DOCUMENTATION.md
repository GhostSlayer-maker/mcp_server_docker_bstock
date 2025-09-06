# Documentación de la API de MCP Service

Esta documentación describe cómo interactuar con la API de MCP Service, diseñada para proporcionar acceso a datos de la base de datos Odoo a través de endpoints HTTP. Es útil tanto para usuarios que deseen entender la funcionalidad como para sistemas automatizados (como IAs) que necesiten integrarse.

## Autenticación

Todas las solicitudes a la API requieren una clave de API para autenticación. Esta clave debe ser proporcionada en el encabezado `X-API-KEY` de cada solicitud.

La clave de API se encuentra en el archivo `.env` del proyecto, bajo la variable `API_KEY`.

Ejemplo de encabezado:

`X-API-KEY: tu-api-key-segura-aqui`

**¡Importante!** Reemplaza `tu-api-key-segura-aqui` con tu clave de API real.

## Endpoints de la API

### 1. Health Check

Verifica el estado del servicio y la conexión a la base de datos.

-   **URL:** `/api/health`
-   **Método:** `GET`
-   **Autenticación:** Requiere `X-API-KEY`

**Ejemplo de Solicitud (cURL):**

```bash
curl -X GET http://localhost:5000/api/health -H 'X-API-KEY: tu-api-key-segura-aqui'
```

**Ejemplo de Solicitud (Python - para IAs/Automatización):**

```python
import requests

api_key = "tu-api-key-segura-aqui"
headers = {"X-API-KEY": api_key}

response = requests.get("http://localhost:5000/api/health", headers=headers)
print(response.json())
```

**Ejemplo de Respuesta Exitosa (JSON):**

```json
{
    "status": "ok",
    "database_connection": "successful"
}
```

### 2. Listar Tablas

Obtiene una lista de todas las tablas disponibles en la base de datos.

-   **URL:** `/api/tables`
-   **Método:** `GET`
-   **Autenticación:** Requiere `X-API-KEY`

**Ejemplo de Solicitud (cURL):**

```bash
curl -X GET http://localhost:5000/api/tables -H 'X-API-KEY: tu-api-key-segura-aqui'
```

**Ejemplo de Solicitud (Python - para IAs/Automatización):**

```python
import requests

api_key = "tu-api-key-segura-aqui"
headers = {"X-API-KEY": api_key}

response = requests.get("http://localhost:5000/api/tables", headers=headers)
print(response.json())
```

**Ejemplo de Respuesta Exitosa (JSON):**

```json
{
    "tables": [
        "ir_act_client",
        "ir_act_report_xml",
        "res_users",
        // ... otras tablas
    ],
    "count": 89
}
```

### 3. Consultar Tabla Específica

Obtiene todos los registros de una tabla específica.

-   **URL:** `/api/query/{table_name}`
-   **Método:** `GET`
-   **Parámetros de Ruta:**
    -   `table_name` (string): El nombre de la tabla a consultar (ej. `res_users`).
-   **Autenticación:** Requiere `X-API-KEY`

**Ejemplo de Solicitud (cURL - para `res_users`):**

```bash
curl -X GET http://localhost:5000/api/query/res_users -H 'X-API-KEY: tu-api-key-segura-aqui'
```

**Ejemplo de Solicitud (Python - para IAs/Automatización):**

```python
import requests

api_key = "tu-api-key-segura-aqui"
headers = {"X-API-KEY": api_key}

table_name = "res_users"
response = requests.get(f"http://localhost:5000/api/query/{table_name}", headers=headers)
print(response.json())
```

**Ejemplo de Respuesta Exitosa (JSON - parcial):**

```json
[
    {
        "id": 3,
        "company_id": 1,
        "partner_id": 3,
        "login": "default",
        // ... otros campos
    },
    // ... otros registros
]
```

### 4. Consulta SQL Personalizada

Permite ejecutar una consulta SQL personalizada en la base de datos. **¡Usar con precaución!**

-   **URL:** `/api/custom_query`
-   **Método:** `POST`
-   **Autenticación:** Requiere `X-API-KEY`
-   **Cuerpo de la Solicitud (JSON):**
    ```json
    {
        "query": "SELECT id, login FROM res_users LIMIT 5"
    }
    ```

**Ejemplo de Solicitud (cURL):**

```bash
curl -X POST http://localhost:5000/api/custom_query \
     -H 'Content-Type: application/json' \
     -H 'X-API-KEY: tu-api-key-segura-aqui' \
     -d '{"query": "SELECT id, login FROM res_users LIMIT 5"}'
```

**Ejemplo de Solicitud (Python - para IAs/Automatización):**

```python
import requests
import json

api_key = "tu-api-key-segura-aqui"
headers = {
    "Content-Type": "application/json",
    "X-API-KEY": api_key
}

query_payload = {"query": "SELECT id, login FROM res_users LIMIT 5"}

response = requests.post(
    "http://localhost:5000/api/custom_query",
    headers=headers,
    data=json.dumps(query_payload)
)
print(response.json())
```

**Ejemplo de Respuesta Exitosa (JSON - parcial):**

```json
{
    "results": [
        {
            "id": 3,
            "login": "default"
        },
        {
            "id": 2,
            "login": "admin"
        }
    ]
}
```

---

Esta documentación proporciona una guía básica para interactuar con la API de MCP Service. Para un uso más avanzado o para resolver problemas, se recomienda revisar el código fuente de la aplicación.