from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from pydantic import UUID4
from pydantic_settings.main import ConfigDict

from utils.formatter import fmt


class BaseSchema(BaseModel):
    id: Optional[UUID4]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    is_deleted: Optional[bool] = None

    class Config:
        from_attributes = True
        validate_assignment: bool = True
        populate_by_name: bool = True
        json_encoders: dict = {datetime: fmt.datetime_to_isoformat}


class BaseSchemaModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        populate_by_name=True,
        json_encoders={datetime: fmt.datetime_to_isoformat},
    )


class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = "success"
    detail: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None


class HTTPError(BaseModel):
    detail: str
