import psycopg2
import toml
from psycopg2.pool import ThreadedConnectionPool

db_pool = None

def init_db_pool():
    """Initializes the database connection pool."""
    global db_pool
    if db_pool is None:
        try:
            with open(".streamlit/secrets.toml", "r") as f:
                secrets = toml.load(f)
            db_config = secrets["postgres"]
            
            # Create a threaded connection pool
            # minconn=1, maxconn=20
            db_pool = ThreadedConnectionPool(1, 20, **db_config)
            print("Database connection pool created.")
            
        except FileNotFoundError:
            print("Error: '.streamlit/secrets.toml' not found.")
            exit(1)
        except KeyError:
            print("Error: 'secrets.toml' is missing the [postgres] section.")
            exit(1)
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error initializing database pool: {error}")
            exit(1)

def get_db_conn():
    """Yields a database connection from the pool."""
    if db_pool is None:
        init_db_pool()
        
    conn = None
    try:
        conn = db_pool.getconn()
        yield conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error getting connection from pool: {error}")
    finally:
        if conn:
            db_pool.putconn(conn)

def close_db_pool():
    """Closes all connections in the pool."""
    global db_pool
    if db_pool:
        db_pool.closeall()
        db_pool = None
        print("Database connection pool closed.")