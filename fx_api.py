import psycopg2
from fastapi import FastAPI, Depends, HTTPException
from typing import List
import schemas
import crud
import database

app = FastAPI()

# --- Database Pool Lifecycle ---

@app.on_event("startup")
def startup_event():
    database.init_db_pool()

@app.on_event("shutdown")
def shutdown_event():
    database.close_db_pool()

# --- Business Vertical Endpoints ---

@app.post("/verticals/", response_model=schemas.BusinessVertical, tags=["Business Verticals"])
def create_vertical(
    vertical: schemas.BusinessVerticalCreate, 
    conn=Depends(database.get_db_conn)
):
    try:
        new_vertical = crud.create_business_vertical(conn=conn, vertical=vertical)
        # Convert to dict for validation
        return schemas.BusinessVertical.model_validate(dict(new_vertical))
    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="Business vertical name already exists.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/verticals/", response_model=List[schemas.BusinessVertical], tags=["Business Verticals"])
def read_verticals(skip: int = 0, limit: int = 100, conn=Depends(database.get_db_conn)):
    verticals_data = crud.get_business_verticals(conn, skip=skip, limit=limit)
    # Convert each item to dict for validation
    return [schemas.BusinessVertical.model_validate(dict(v)) for v in verticals_data]

@app.get("/verticals/{vertical_id}", response_model=schemas.BusinessVertical, tags=["Business Verticals"])
def read_vertical(vertical_id: int, conn=Depends(database.get_db_conn)):
    db_vertical = crud.get_business_vertical(conn=conn, vertical_id=vertical_id)
    if db_vertical is None:
        raise HTTPException(status_code=404, detail="Business vertical not found")
    return schemas.BusinessVertical.model_validate(dict(db_vertical))

@app.put("/verticals/{vertical_id}", response_model=schemas.BusinessVertical, tags=["Business Verticals"])
def update_vertical(
    vertical_id: int, 
    vertical: schemas.BusinessVerticalCreate, 
    conn=Depends(database.get_db_conn)
):
    try:
        updated_vertical = crud.update_business_vertical(conn, vertical_id, vertical)
        if updated_vertical is None:
            raise HTTPException(status_code=404, detail="Business vertical not found")
        return schemas.BusinessVertical.model_validate(dict(updated_vertical))
    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="Business vertical name already exists.")

@app.delete("/verticals/{vertical_id}", response_model=schemas.BusinessVertical, tags=["Business Verticals"])
def delete_vertical(vertical_id: int, conn=Depends(database.get_db_conn)):
    try:
        deleted_vertical = crud.delete_business_vertical(conn, vertical_id)
        if deleted_vertical is None:
            raise HTTPException(status_code=404, detail="Business vertical not found")
        return schemas.BusinessVertical.model_validate(dict(deleted_vertical))
    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(status_code=400, detail="Cannot delete vertical, it is referenced by business units.")

# --- Business Unit Endpoints ---

@app.post("/units/", response_model=schemas.BusinessUnit, tags=["Business Units"])
def create_unit(
    unit: schemas.BusinessUnitCreate, 
    conn=Depends(database.get_db_conn)
):
    try:
        new_unit = crud.create_business_unit(conn=conn, unit=unit)
        return schemas.BusinessUnit.model_validate(dict(new_unit))
    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="Business unit name already exists.")
    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(status_code=404, detail="Business vertical not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/units/", response_model=List[schemas.BusinessUnit], tags=["Business Units"])
def read_units(skip: int = 0, limit: int = 100, conn=Depends(database.get_db_conn)):
    units_data = crud.get_business_units(conn, skip=skip, limit=limit)
    return [schemas.BusinessUnit.model_validate(dict(u)) for u in units_data]

@app.get("/units/{unit_id}", response_model=schemas.BusinessUnit, tags=["Business Units"])
def read_unit(unit_id: int, conn=Depends(database.get_db_conn)):
    db_unit = crud.get_business_unit(conn=conn, unit_id=unit_id)
    if db_unit is None:
        raise HTTPException(status_code=44, detail="Business unit not found")
    return schemas.BusinessUnit.model_validate(dict(db_unit))

@app.put("/units/{unit_id}", response_model=schemas.BusinessUnit, tags=["Business Units"])
def update_unit(
    unit_id: int, 
    unit: schemas.BusinessUnitCreate, 
    conn=Depends(database.get_db_conn)
):
    try:
        updated_unit = crud.update_business_unit(conn, unit_id, unit)
        if updated_unit is None:
            raise HTTPException(status_code=404, detail="Business unit not found")
        return schemas.BusinessUnit.model_validate(dict(updated_unit))
    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="Business unit name already exists.")
    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(status_code=404, detail="Business vertical not found.")

@app.delete("/units/{unit_id}", response_model=schemas.BusinessUnit, tags=["Business Units"])
def delete_unit(unit_id: int, conn=Depends(database.get_db_conn)):
    try:
        deleted_unit = crud.delete_business_unit(conn, unit_id)
        if deleted_unit is None:
            raise HTTPException(status_code=404, detail="Business unit not found")
        return schemas.BusinessUnit.model_validate(dict(deleted_unit))
    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(status_code=400, detail="Cannot delete unit, it is referenced by clients.")

# --- Client Endpoints ---

@app.post("/clients/", response_model=schemas.Client, tags=["Clients"])
def create_client(
    client: schemas.ClientCreate, 
    conn=Depends(database.get_db_conn)
):
    try:
        new_client = crud.create_client(conn=conn, client=client)
        return schemas.Client.model_validate(dict(new_client))
    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="Client name already exists.")
    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(status_code=404, detail="Business unit not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/clients/", response_model=List[schemas.Client], tags=["Clients"])
def read_clients(skip: int = 0, limit: int = 100, conn=Depends(database.get_db_conn)):
    clients_data = crud.get_clients(conn, skip=skip, limit=limit)
    return [schemas.Client.model_validate(dict(c)) for c in clients_data]

@app.get("/clients/{client_id}", response_model=schemas.Client, tags=["Clients"])
def read_client(client_id: int, conn=Depends(database.get_db_conn)):
    db_client = crud.get_client(conn=conn, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return schemas.Client.model_validate(dict(db_client))

@app.put("/clients/{client_id}", response_model=schemas.Client, tags=["Clients"])
def update_client(
    client_id: int, 
    client: schemas.ClientCreate, 
    conn=Depends(database.get_db_conn)
):
    try:
        updated_client = crud.update_client(conn, client_id, client)
        if updated_client is None:
            raise HTTPException(status_code=404, detail="Client not found")
        return schemas.Client.model_validate(dict(updated_client))
    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="Client name already exists.")
    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(status_code=404, detail="Business unit not found.")

@app.delete("/clients/{client_id}", response_model=schemas.Client, tags=["Clients"])
def delete_client(client_id: int, conn=Depends(database.get_db_conn)):
    try:
        deleted_client = crud.delete_client(conn, client_id)
        if deleted_client is None:
            raise HTTPException(status_code=44, detail="Client not found")
        return schemas.Client.model_validate(dict(deleted_client))
    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(status_code=400, detail="Cannot delete client, it is referenced by forecasts.")

# --- Work Type Endpoints ---

@app.get("/work_types/", response_model=List[schemas.WorkType], tags=["Work Types"])
def read_work_types(skip: int = 0, limit: int = 100, conn=Depends(database.get_db_conn)):
    work_types_data = crud.get_work_types(conn, skip=skip, limit=limit)
    return [schemas.WorkType.model_validate(dict(w)) for w in work_types_data]

@app.post("/work_types/", response_model=schemas.WorkType, tags=["Work Types"])
def create_work_type(
    work_type: schemas.WorkTypeCreate, 
    conn=Depends(database.get_db_conn)
):
    try:
        new_work_type = crud.create_work_type(conn=conn, work_type=work_type)
        return schemas.WorkType.model_validate(dict(new_work_type))
    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="Work type name already exists.")
    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(status_code=404, detail="Work type origin not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/work_types/{work_type_id}", response_model=schemas.WorkType, tags=["Work Types"])
def update_work_type(
    work_type_id: int, 
    work_type: schemas.WorkTypeCreate, 
    conn=Depends(database.get_db_conn)
):
    try:
        updated_work_type = crud.update_work_type(conn, work_type_id, work_type)
        if updated_work_type is None:
            raise HTTPException(status_code=404, detail="Work type not found")
        return schemas.WorkType.model_validate(dict(updated_work_type))
    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="Work type name already exists.")
    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(status_code=404, detail="Work type origin not found.")

@app.delete("/work_types/{work_type_id}", response_model=schemas.WorkType, tags=["Work Types"])
def delete_work_type(work_type_id: int, conn=Depends(database.get_db_conn)):
    try:
        deleted_work_type = crud.delete_work_type(conn, work_type_id)
        if deleted_work_type is None:
            raise HTTPException(status_code=404, detail="Work type not found")
        return schemas.WorkType.model_validate(dict(deleted_work_type))
    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(status_code=400, detail="Cannot delete work type, it is referenced by forecasts.")

# --- Work Type Origin Type Endpoints ---

@app.get("/work_type_origin_types/", response_model=List[schemas.WorkTypeOriginType], tags=["Work Type Origins"])
def read_work_type_origin_types(skip: int = 0, limit: int = 100, conn=Depends(database.get_db_conn)):
    origin_types = crud.get_work_type_origin_types(conn, skip=skip, limit=limit)
    return [schemas.WorkTypeOriginType.model_validate(dict(o)) for o in origin_types]

@app.post("/work_type_origin_types/", response_model=schemas.WorkTypeOriginType, tags=["Work Type Origins"])
def create_work_type_origin_type(
    origin_type: schemas.WorkTypeOriginTypeCreate, 
    conn=Depends(database.get_db_conn)
):
    try:
        new_origin_type = crud.create_work_type_origin_type(conn=conn, origin_type=origin_type)
        return schemas.WorkTypeOriginType.model_validate(dict(new_origin_type))
    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="Work type origin name already exists.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/work_type_origin_types/{origin_type_id}", response_model=schemas.WorkTypeOriginType, tags=["Work Type Origins"])
def update_work_type_origin_type(
    origin_type_id: int, 
    origin_type: schemas.WorkTypeOriginTypeCreate, 
    conn=Depends(database.get_db_conn)
):
    try:
        updated_origin_type = crud.update_work_type_origin_type(conn, origin_type_id, origin_type)
        if updated_origin_type is None:
            raise HTTPException(status_code=404, detail="Work type origin not found")
        return schemas.WorkTypeOriginType.model_validate(dict(updated_origin_type))
    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="Work type origin name already exists.")

@app.delete("/work_type_origin_types/{origin_type_id}", response_model=schemas.WorkTypeOriginType, tags=["Work Type Origins"])
def delete_work_type_origin_type(origin_type_id: int, conn=Depends(database.get_db_conn)):
    try:
        deleted_origin_type = crud.delete_work_type_origin_type(conn, origin_type_id)
        if deleted_origin_type is None:
            raise HTTPException(status_code=404, detail="Work type origin not found")
        return schemas.WorkTypeOriginType.model_validate(dict(deleted_origin_type))
    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(status_code=400, detail="Cannot delete, it is referenced by work types.")


# --- Forecast Endpoints ---

@app.get("/forecasts/", response_model=List[schemas.ForecastDetail], tags=["Forecasts"])
def read_forecasts(skip: int = 0, limit: int = 100, conn=Depends(database.get_db_conn)):
    """
    Get all forecasts with joined data for display.
    """
    forecasts = crud.get_forecasts(conn, skip=skip, limit=limit)
    # Parse raw dict rows into the detail schema
    return [schemas.ForecastDetail.model_validate(dict(f)) for f in forecasts]

@app.post("/forecasts/", response_model=schemas.Forecast, tags=["Forecasts"])
def create_forecast(
    forecast: schemas.ForecastCreate, 
    conn=Depends(database.get_db_conn)
):
    try:
        new_forecast = crud.create_forecast(conn=conn, forecast=forecast)
        return schemas.Forecast.model_validate(dict(new_forecast))
    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="This forecast (client, BU, work type, date) already exists.")
    except psycopg2.errors.ForeignKeyViolation as e:
        raise HTTPException(status_code=404, detail=f"Invalid foreign key: {e.diag.constraint_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/forecasts/{forecast_id}", response_model=schemas.Forecast, tags=["Forecasts"])
def update_forecast(
    forecast_id: int, 
    forecast_update: schemas.ForecastUpdate, 
    conn=Depends(database.get_db_conn)
):
    """
    Update a forecast's amount.
    """
    updated_forecast = crud.update_forecast_amount(conn, forecast_id, forecast_update)
    if updated_forecast is None:
        raise HTTPException(status_code=404, detail="Forecast not found")
    return schemas.Forecast.model_validate(dict(updated_forecast))

@app.delete("/forecasts/{forecast_id}", response_model=schemas.Forecast, tags=["Forecasts"])
def delete_forecast(forecast_id: int, conn=Depends(database.get_db_conn)):
    deleted_forecast = crud.delete_forecast(conn, forecast_id)
    if deleted_forecast is None:
        raise HTTPException(status_code=404, detail="Forecast not found")
    return schemas.Forecast.model_validate(dict(deleted_forecast))