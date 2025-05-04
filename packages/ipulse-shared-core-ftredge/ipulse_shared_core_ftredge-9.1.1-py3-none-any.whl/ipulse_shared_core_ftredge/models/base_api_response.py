from typing import Generic, TypeVar, Optional, Any, Dict, List
import datetime as dt
import json
from pydantic import BaseModel, ConfigDict
from fastapi.responses import JSONResponse
from ipulse_shared_core_ftredge.utils import CustomJSONEncoder


T = TypeVar('T')

class BaseAPIResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[str] = None

    metadata: Dict[str, Any] = {
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat()
    }

class PaginatedAPIResponse(BaseAPIResponse, Generic[T]):
    total_count: int
    page: int
    page_size: int
    items: List[T]

class CustomJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        # Handle Pydantic models to exclude computed fields
        if isinstance(content, dict) and "data" in content and hasattr(content["data"], "model_dump"):
            # If content["data"] is a Pydantic model, use model_dump with exclude_unset=True
            # and exclude_computed=True to prevent serialization of computed fields
            content = dict(content)  # Create a copy to avoid modifying the original
            content["data"] = content["data"].model_dump(
                exclude_unset=True,
                exclude_computed=True
            )

        # Use the CustomJSONEncoder for serialization
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            default=CustomJSONEncoder().default
        ).encode("utf-8")