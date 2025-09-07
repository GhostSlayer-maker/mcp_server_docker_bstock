import os
import sys
import psycopg2
from psycopg2 import extras
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_db_connection():
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            user=os.getenv('DB_USER', 'odoo'),
            password=os.getenv('DB_PASSWORD', 'odoo17@2023'),
            dbname=os.getenv('DB_NAME', 'postgres'),
            cursor_factory=extras.RealDictCursor
        )
        
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('ir_module_module', 'res_users')
                );
            """)
            tables_exist = cur.fetchone()['exists']
            
            if not tables_exist:
                logger.error("Odoo tables not found")
                return False
                
            logger.info("Database health check passed successfully")
            return True
    except Exception as e:
        logger.error(f"Healthcheck failed: {str(e)}", exc_info=True)
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    try:
        if check_db_connection():
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in health check: {str(e)}", exc_info=True)
        sys.exit(1)