from psycopg2.extras import DictCursor
import schemas
from datetime import date

# Helper to convert DictRow to a Pydantic model
def model_from_dictrow(model_class, dict_row):
    if dict_row:
        # CONVERT TO DICT FIRST! This is the fix.
        return model_class(**dict(dict_row))
    return None

# --- Business Vertical CRUD ---

def create_business_vertical(conn, vertical: schemas.BusinessVerticalCreate):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(
            "INSERT INTO business_vertical (business_vertical_name) VALUES (%s) RETURNING *",
            (vertical.business_vertical_name,)
        )
        new_vertical = cur.fetchone()
        conn.commit()
        return new_vertical # Return raw data

def get_business_vertical(conn, vertical_id: int):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT * FROM business_vertical WHERE business_vertical_id = %s", (vertical_id,))
        vertical = cur.fetchone()
        return vertical # Return raw data

def get_business_verticals(conn, skip: int = 0, limit: int = 100):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT * FROM business_vertical LIMIT %s OFFSET %s", (limit, skip))
        verticals = cur.fetchall()
        return verticals # Return raw data

def update_business_vertical(conn, vertical_id: int, vertical: schemas.BusinessVerticalCreate):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(
            "UPDATE business_vertical SET business_vertical_name = %s WHERE business_vertical_id = %s RETURNING *",
            (vertical.business_vertical_name, vertical_id)
        )
        updated_vertical = cur.fetchone()
        conn.commit()
        return updated_vertical # Return raw data

def delete_business_vertical(conn, vertical_id: int):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("DELETE FROM business_vertical WHERE business_vertical_id = %s RETURNING *", (vertical_id,))
        deleted_vertical = cur.fetchone()
        conn.commit()
        return deleted_vertical # Return raw data

# --- Business Unit CRUD ---

def create_business_unit(conn, unit: schemas.BusinessUnitCreate):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(
            "INSERT INTO business_unit (business_unit_name, business_vertical_id) VALUES (%s, %s) RETURNING *",
            (unit.business_unit_name, unit.business_vertical_id)
        )
        new_unit = cur.fetchone()
        conn.commit()
        return new_unit # Return raw data

def get_business_unit(conn, unit_id: int):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT * FROM business_unit WHERE business_unit_id = %s", (unit_id,))
        unit = cur.fetchone()
        return unit # Return raw data

def get_business_units(conn, skip: int = 0, limit: int = 100):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT * FROM business_unit LIMIT %s OFFSET %s", (limit, skip))
        units = cur.fetchall()
        return units # Return raw data

def update_business_unit(conn, unit_id: int, unit: schemas.BusinessUnitCreate):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(
            "UPDATE business_unit SET business_unit_name = %s, business_vertical_id = %s WHERE business_unit_id = %s RETURNING *",
            (unit.business_unit_name, unit.business_vertical_id, unit_id)
        )
        updated_unit = cur.fetchone()
        conn.commit()
        return updated_unit # Return raw data

def delete_business_unit(conn, unit_id: int):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("DELETE FROM business_unit WHERE business_unit_id = %s RETURNING *", (unit_id,))
        deleted_unit = cur.fetchone()
        conn.commit()
        return deleted_unit # Return raw data

# --- Client CRUD ---

def create_client(conn, client: schemas.ClientCreate):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(
            """
            INSERT INTO clients (client_name, client_active, client_start_date, client_end_date, business_unit_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
            """,
            (client.client_name, client.client_active, client.client_start_date, client.client_end_date, client.business_unit_id)
        )
        new_client = cur.fetchone()
        conn.commit()
        return new_client # Return raw data

def get_client(conn, client_id: int):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT * FROM clients WHERE client_id = %s", (client_id,))
        client = cur.fetchone()
        return client # Return raw data

def get_clients(conn, skip: int = 0, limit: int = 100):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT * FROM clients LIMIT %s OFFSET %s", (limit, skip))
        clients = cur.fetchall()
        return clients # Return raw data

def update_client(conn, client_id: int, client: schemas.ClientCreate):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(
            """
            UPDATE clients
            SET client_name = %s, client_active = %s, client_start_date = %s, client_end_date = %s, business_unit_id = %s
            WHERE client_id = %s
            RETURNING *
            """,
            (client.client_name, client.client_active, client.client_start_date, client.client_end_date, client.business_unit_id, client_id)
        )
        updated_client = cur.fetchone()
        conn.commit()
        return updated_client # Return raw data

def delete_client(conn, client_id: int):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("DELETE FROM clients WHERE client_id = %s RETURNING *", (client_id,))
        deleted_client = cur.fetchone()
        conn.commit()
        return deleted_client # Return raw data

# --- Work Type CRUD ---

def create_work_type(conn, work_type: schemas.WorkTypeCreate):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(
            "INSERT INTO work_type (work_type_name, work_type_origin_type_id) VALUES (%s, %s) RETURNING *",
            (work_type.work_type_name, work_type.work_type_origin_type_id)
        )
        new_work_type = cur.fetchone()
        conn.commit()
        return new_work_type # Return raw data

def get_work_type(conn, work_type_id: int):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT * FROM work_type WHERE work_type_id = %s", (work_type_id,))
        work_type = cur.fetchone()
        return work_type # Return raw data

def get_work_types(conn, skip: int = 0, limit: int = 100):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT * FROM work_type LIMIT %s OFFSET %s", (limit, skip))
        work_types = cur.fetchall()
        return work_types # Return raw data

def update_work_type(conn, work_type_id: int, work_type: schemas.WorkTypeCreate):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(
            "UPDATE work_type SET work_type_name = %s, work_type_origin_type_id = %s WHERE work_type_id = %s RETURNING *",
            (work_type.work_type_name, work_type.work_type_origin_type_id, work_type_id)
        )
        updated_work_type = cur.fetchone()
        conn.commit()
        return updated_work_type

def delete_work_type(conn, work_type_id: int):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("DELETE FROM work_type WHERE work_type_id = %s RETURNING *", (work_type_id,))
        deleted_work_type = cur.fetchone()
        conn.commit()
        return deleted_work_type

# --- Work Type Origin Type CRUD ---

def get_work_type_origin_type(conn, origin_type_id: int):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT * FROM work_type_origin_type WHERE work_type_origin_type_id = %s", (origin_type_id,))
        origin_type = cur.fetchone()
        return origin_type

def get_work_type_origin_types(conn, skip: int = 0, limit: int = 100):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT * FROM work_type_origin_type LIMIT %s OFFSET %s", (limit, skip))
        origin_types = cur.fetchall()
        return origin_types

def create_work_type_origin_type(conn, origin_type: schemas.WorkTypeOriginTypeCreate):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(
            "INSERT INTO work_type_origin_type (work_type_origin_type_name) VALUES (%s) RETURNING *",
            (origin_type.work_type_origin_type_name,)
        )
        new_origin_type = cur.fetchone()
        conn.commit()
        return new_origin_type

def update_work_type_origin_type(conn, origin_type_id: int, origin_type: schemas.WorkTypeOriginTypeCreate):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(
            "UPDATE work_type_origin_type SET work_type_origin_type_name = %s WHERE work_type_origin_type_id = %s RETURNING *",
            (origin_type.work_type_origin_type_name, origin_type_id)
        )
        updated_origin_type = cur.fetchone()
        conn.commit()
        return updated_origin_type

def delete_work_type_origin_type(conn, origin_type_id: int):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("DELETE FROM work_type_origin_type WHERE work_type_origin_type_id = %s RETURNING *", (origin_type_id,))
        deleted_origin_type = cur.fetchone()
        conn.commit()
        return deleted_origin_type

# --- Forecast CRUD ---

def get_forecasts(conn, skip: int = 0, limit: int = 100):
    """
    Fetches all forecasts with joined names for detailed view.
    """
    query = """
    SELECT 
        f.forecast_id,
        bv.business_vertical_name,
        bu.business_unit_name,
        c.client_name,
        wt.work_type_name,
        f.dt,
        f.forecast_amount
    FROM 
        forecasts f
    JOIN 
        clients c ON f.client_id = c.client_id
    JOIN 
        work_type wt ON f.work_type_id = wt.work_type_id
    JOIN
        business_unit bu ON f.business_unit_id = bu.business_unit_id
    JOIN
        business_vertical bv ON bu.business_vertical_id = bv.business_vertical_id
    ORDER BY
        bv.business_vertical_name, bu.business_unit_name, c.client_name, wt.work_type_name, f.dt
    LIMIT %s OFFSET %s;
    """
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(query, (limit, skip))
        forecasts = cur.fetchall()
        # We return the raw DictRow, main.py will parse into schema
        return forecasts

def create_forecast(conn, forecast: schemas.ForecastCreate):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(
            """
            INSERT INTO forecasts (
                client_id, business_unit_id, work_type_id, dt, 
                forecast_amount, forecast_name
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                forecast.client_id, forecast.business_unit_id, forecast.work_type_id,
                forecast.dt, forecast.forecast_amount, forecast.forecast_name
            )
        )
        new_forecast = cur.fetchone()
        conn.commit()
        return new_forecast # Return raw data

def update_forecast_amount(conn, forecast_id: int, forecast_update: schemas.ForecastUpdate):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(
            "UPDATE forecasts SET forecast_amount = %s WHERE forecast_id = %s RETURNING *",
            (forecast_update.forecast_amount, forecast_id)
        )
        updated_forecast = cur.fetchone()
        conn.commit()
        return updated_forecast # Return raw data

def delete_forecast(conn, forecast_id: int):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("DELETE FROM forecasts WHERE forecast_id = %s RETURNING *", (forecast_id,))
        deleted_forecast = cur.fetchone()
        conn.commit()
        return deleted_forecast # Return raw data