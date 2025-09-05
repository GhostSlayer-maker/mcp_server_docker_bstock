import os
import sys
import psycopg2
from psycopg2 import extras

def check_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            user=os.getenv('DB_USER', 'odoo'),
            password=os.getenv('DB_PASSWORD', 'odoo17@2023'),
            dbname=os.getenv('DB_NAME', 'postgres'),
            cursor_factory=extras.RealDictCursor
        )
        
        with conn.cursor() as cur:
            # Verificar si las tablas principales de Odoo existen
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('ir_module_module', 'res_users')
                );
            """)
            tables_exist = cur.fetchone()['exists']
            
            if not tables_exist:
                print("Odoo tables not found", file=sys.stderr)
                return False
                
        conn.close()
        return True
    except Exception as e:
        print(f"Healthcheck failed: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    if check_db_connection():
        sys.exit(0)
    else:
        sys.exit(1)