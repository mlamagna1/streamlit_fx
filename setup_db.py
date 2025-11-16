import psycopg2
import toml
import datetime

# --- Load Secrets ---
try:
    with open(".streamlit/secrets.toml", "r") as f:
        secrets = toml.load(f)
    db_config = secrets["postgres"]
    print("Loaded database configuration from secrets.toml")
except FileNotFoundError:
    print("Error: '.streamlit/secrets.toml' not found.")
    print("Please create it with your PostgreSQL credentials.")
    exit(1)
except KeyError:
    print("Error: 'secrets.toml' is missing the [postgres] section.")
    exit(1)

# --- SQL Commands to Create Tables (Corrected Order) ---
CREATE_TABLES_SQL = """
-- Drop tables in reverse order of creation to respect foreign keys
DROP TABLE IF EXISTS forecasts;
DROP TABLE IF EXISTS clients;
DROP TABLE IF EXISTS work_type;
DROP TABLE IF EXISTS business_unit;
DROP TABLE IF EXISTS work_type_origin_type;
DROP TABLE IF EXISTS business_vertical;

-- Create tables in order of dependency
CREATE TABLE business_vertical (
    business_vertical_id SERIAL PRIMARY KEY,
    business_vertical_name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE work_type_origin_type (
    work_type_origin_type_id SERIAL PRIMARY KEY,
    work_type_origin_type_name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE business_unit (
    business_unit_id SERIAL PRIMARY KEY,
    business_unit_name VARCHAR(255) UNIQUE NOT NULL,
    business_vertical_id INT NOT NULL REFERENCES business_vertical(business_vertical_id)
);

CREATE TABLE work_type (
    work_type_id SERIAL PRIMARY KEY,
    work_type_name VARCHAR(255) UNIQUE NOT NULL,
    work_type_origin_type_id INT NOT NULL REFERENCES work_type_origin_type(work_type_origin_type_id)
);

CREATE TABLE clients (
    client_id SERIAL PRIMARY KEY,
    client_name VARCHAR(255) UNIQUE NOT NULL,
    client_active BOOLEAN DEFAULT TRUE,
    client_start_date DATE NOT NULL,
    client_end_date DATE,
    business_unit_id INT NOT NULL REFERENCES business_unit(business_unit_id)
);

CREATE TABLE forecasts (
    forecast_id SERIAL PRIMARY KEY,
    forecast_name VARCHAR(255), -- Removed UNIQUE NOT NULL, seems complex for sample data
    client_id INT NOT NULL REFERENCES clients(client_id),
    business_unit_id INT NOT NULL REFERENCES business_unit(business_unit_id),
    work_type_id INT NOT NULL REFERENCES work_type(work_type_id),
    dt DATE NOT NULL,
    forecast_amount INT NOT NULL,
    -- This constraint ensures a unique forecast entry per client, BU, work type, and day
    CONSTRAINT unique_forecast UNIQUE(business_unit_id, client_id, work_type_id, dt)
);

CREATE INDEX idx_dt ON forecasts(dt);
"""

# --- SQL Commands to Insert Sample Data (Corrected and Expanded) ---
INSERT_SAMPLE_DATA_SQL = """
-- 1. Populate tables with no dependencies
INSERT INTO business_vertical (business_vertical_name) VALUES
('Technology'),
('Finance'),
('Healthcare');

INSERT INTO work_type_origin_type (work_type_origin_type_name) VALUES
('Internal Project'),
('Client Request');

-- 2. Populate tables with dependencies
INSERT INTO business_unit (business_unit_name, business_vertical_id) VALUES
('Consulting Services', 1),  -- Tech
('Managed Services', 1),     -- Tech
('Investment Banking', 2),   -- Finance
('Data Science', 3);         -- Healthcare

INSERT INTO work_type (work_type_name, work_type_origin_type_id) VALUES
('Consulting', 2),
('Development', 1),
('Support', 2),
('Data Analysis', 2);

-- 3. Populate clients
INSERT INTO clients (client_name, client_active, client_start_date, business_unit_id) VALUES
('Acme Corp', TRUE, '2023-01-01', 1),
('Beta Industries', TRUE, '2024-05-15', 2),
('Gamma Solutions', FALSE, '2022-03-10', 1);

-- 4. Populate forecasts
-- Sample data for Acme Corp (Client 1, BU 1)
INSERT INTO forecasts (client_id, business_unit_id, work_type_id, dt, forecast_amount) VALUES
(1, 1, 1, '2025-11-01', 10000),
(1, 1, 1, '2025-12-01', 12000),
(1, 1, 1, '2026-01-01', 11000),
(1, 1, 2, '2025-11-01', 25000),
(1, 1, 2, '2025-12-01', 22000),
(1, 1, 2, '2026-01-01', 27000);

-- Sample data for Beta Industries (Client 2, BU 2)
INSERT INTO forecasts (client_id, business_unit_id, work_type_id, dt, forecast_amount) VALUES
(2, 2, 3, '2025-11-01', 5000),
(2, 2, 3, '2025-12-01', 5000),
(2, 2, 3, '2026-01-01', 5500),
(2, 2, 4, '2025-11-01', 8000),
(2, 2, 4, '2025-12-01', 9000);
"""

def setup_database():
    """Connects to Postgres, drops old tables, creates new ones, and inserts sample data."""
    conn = None
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_config)
        with conn.cursor() as cur:
            # Create tables
            print("Dropping old tables and creating new ones...")
            cur.execute(CREATE_TABLES_SQL)
            print("Tables created successfully.")
            
            # Insert sample data
            print("Inserting sample data...")
            cur.execute(INSERT_SAMPLE_DATA_SQL)
            print("Sample data inserted.")
        
        # Commit the transaction
        conn.commit()
        print("\n--- Database setup complete! ---")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error during database setup: {error}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    setup_database()