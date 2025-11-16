from pydantic import BaseModel
from datetime import date

# --- Business Vertical Schemas ---

class BusinessVerticalBase(BaseModel):
    business_vertical_name: str

class BusinessVerticalCreate(BusinessVerticalBase):
    pass

class BusinessVertical(BusinessVerticalBase):
    business_vertical_id: int

    class Config:
        from_attributes = True

# --- Business Unit Schemas ---

class BusinessUnitBase(BaseModel):
    business_unit_name: str
    business_vertical_id: int

class BusinessUnitCreate(BusinessUnitBase):
    pass

class BusinessUnit(BusinessUnitBase):
    business_unit_id: int

    class Config:
        from_attributes = True

# --- Client Schemas ---

class ClientBase(BaseModel):
    client_name: str
    client_active: bool | None = True
    client_start_date: date
    client_end_date: date | None = None
    business_unit_id: int

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    client_id: int

    class Config:
        from_attributes = True

# --- Work Type Origin Schemas ---

class WorkTypeOriginTypeBase(BaseModel):
    work_type_origin_type_name: str

class WorkTypeOriginTypeCreate(WorkTypeOriginTypeBase):
    pass

class WorkTypeOriginType(WorkTypeOriginTypeBase):
    work_type_origin_type_id: int

    class Config:
        from_attributes = True

# --- Work Type Schemas ---

class WorkTypeBase(BaseModel):
    work_type_name: str
    work_type_origin_type_id: int

class WorkTypeCreate(WorkTypeBase):
    pass

class WorkType(WorkTypeBase):
    work_type_id: int

    class Config:
        from_attributes = True

# --- Forecast Schemas ---

class ForecastBase(BaseModel):
    client_id: int
    business_unit_id: int
    work_type_id: int
    dt: date
    forecast_amount: int
    forecast_name: str | None = None

class ForecastCreate(ForecastBase):
    pass

class Forecast(ForecastBase):
    forecast_id: int

    class Config:
        from_attributes = True

class ForecastUpdate(BaseModel):
    """Schema specifically for updating only the amount."""
    forecast_amount: int

class ForecastDetail(BaseModel):
    """Schema for returning joined forecast data."""
    forecast_id: int
    business_vertical_name: str
    business_unit_name: str
    client_name: str
    work_type_name: str
    dt: date
    forecast_amount: int

    class Config:
        from_attributes = True