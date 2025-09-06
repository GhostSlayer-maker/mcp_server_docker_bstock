import os
import os
import psycopg2
from psycopg2 import extras
from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from psycopg2 import sql
from fastapi.security import APIKeyHeader
import logging
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MCP Server",
    description="Model Context Protocol Server for Odoo",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Seguridad: API Key
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != os.getenv("API_KEY", "your-secret-key"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return api_key

# Función para conectar a la base de datos
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            user=os.getenv('DB_USER', 'odoo'),
            password=os.getenv('DB_PASSWORD', 'odoo17@2023'),
            dbname=os.getenv('DB_NAME', 'postgres'),
            cursor_factory=extras.RealDictCursor
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}", exc_info=True)
        return None

# Endpoint de health check
# GET /api/health
# Verifica la conexión con la base de datos
# Respuesta exitosa: {"status": "healthy", "database": "connected"}
# Respuesta de error: HTTP 500 si falla la conexión a la base de datos
@app.get("/api/health")
async def health_check(api_key: str = Depends(get_api_key)):
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
            if result['?column?'] == 1:
                return {"status": "ok", "database_connection": "successful"}
            else:
                raise HTTPException(status_code=500, detail="Database query failed")
    except Exception as e:
        logger.error(f"Error in health check: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Endpoint para listar tablas
# GET /api/tables
# Lista todas las tablas de Odoo que empiezan con 'ir_' o 'res_'
# Respuesta exitosa: {"tables": ["nombre_tabla1", "nombre_tabla2", ...], "count": numero_total}
# Respuesta de error: HTTP 500 si hay error en la base de datos
@app.get("/api/tables", dependencies=[Depends(get_api_key)])
async def list_tables():
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            # Consulta para obtener todas las tablas de Odoo
            query = sql.SQL("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND (table_name LIKE 'ir_%'
                OR table_name LIKE 'res_%')
                ORDER BY table_name;
            """)
            logger.info(f"Executing query: {query.as_string(conn)}")
            cur.execute(query)
            rows = cur.fetchall()
            logger.info(f"Raw query results: {rows}")
            tables = [row['table_name'] for row in rows] if rows else []
            logger.info(f"Found {len(tables)} tables: {tables}")
            return {"tables": tables, "count": len(tables)}
    except Exception as e:
        logger.error(f"Error listing tables: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

# Modelo para la respuesta de la tabla
class TableData(BaseModel):
    table_name: str
    data: list

# Endpoint para obtener los primeros 10 registros de una tabla
# GET /api/query/{table_name}
# Obtiene los primeros 10 registros de la tabla especificada
# Parámetros:
#   - table_name: Nombre de la tabla a consultar
# Respuesta exitosa: {"table_name": "nombre_tabla", "data": [{campo1: valor1, ...}, ...]}
# Respuesta de error:
#   - HTTP 404 si la tabla no existe
#   - HTTP 500 si hay error en la base de datos
@app.get("/api/query/{table_name}", response_model=TableData, dependencies=[Depends(get_api_key)])
async def query_table(table_name: str):
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        with conn.cursor() as cur:
            # Verificar que la tabla existe
            check_table_query = sql.SQL("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """)
            cur.execute(check_table_query, (table_name,))
            result = cur.fetchone()
            table_exists = bool(result)
            
            if not table_exists:
                raise HTTPException(status_code=404, detail=f"Table {table_name} not found")
            
            # Obtener los primeros 10 registros
            query_data = sql.SQL("SELECT * FROM {} LIMIT %s;").format(sql.Identifier(table_name))
            cur.execute(query_data, (10,))
            data = cur.fetchall()
            return TableData(table_name=table_name, data=data)
            
            
            

    except Exception as e:
        logger.error(f"Error querying table {table_name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Modelo para consultas personalizadas
class CustomQuery(BaseModel):
    query: str
    params: Optional[List[Any]] = None
    limit: Optional[int] = 100

# Endpoint para consultas personalizadas
# POST /api/custom_query
# Ejecuta una consulta SQL personalizada (solo SELECT)
# Cuerpo de la petición (JSON):
# {
#   "query": "SELECT campo1, campo2 FROM tabla WHERE condicion",
#   "params": [param1, param2, ...] (opcional),
#   "limit": numero_maximo_registros (opcional, default: 100)
# }
# Ejemplo de uso con PowerShell:
# $body = @{
#   query = 'SELECT name, email FROM res_partner LIMIT 5'
#   params = @()
#   limit = 5
# } | ConvertTo-Json
# Invoke-RestMethod -Uri 'http://localhost:5000/api/custom_query' -Method Post -ContentType 'application/json' -Body $body
#
# Respuesta exitosa: {"results": [{campo1: valor1, ...}, ...]}
# Respuesta de error:
#   - HTTP 400 si la consulta no es SELECT
#   - HTTP 500 si hay error en la base de datos
@app.post("/api/custom_query", dependencies=[Depends(get_api_key)])
async def execute_custom_query(query_data: CustomQuery):
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        with conn.cursor() as cur:
            # Validar que la consulta sea de solo lectura
            if not query_data.query.lower().strip().startswith('select'):
                raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")
            
            # Agregar límite a la consulta si no está presente
            query = query_data.query
            if 'limit' not in query.lower():
                query += f" LIMIT {query_data.limit}"
            
            # Ejecutar la consulta
            if query_data.params:
                cur.execute(sql.SQL(query), query_data.params)
            else:
                logger.info(f"Executing custom query: {query}")
                cur.execute(sql.SQL(query))
            
            # Obtener los resultados
            results = cur.fetchmany(query_data.limit)
            logger.info(f"Custom query returned {len(results)} results.")
            return {"results": results}
            
    except Exception as e:
        logger.error(f"Error executing custom query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Punto de entrada para ejecutar el servidor
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)