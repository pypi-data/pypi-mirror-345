import os
import logging
from typing import Optional, Iterable, Dict, Any, List
from datetime import datetime, timedelta, timezone
import httpx
from fastapi import HTTPException, Request
from google.cloud import firestore
from ipulse_shared_core_ftredge.services import ServiceError, AuthorizationError, ResourceNotFoundError
from ipulse_shared_core_ftredge.models import UserStatus

# Constants
USERS_STATUS_COLLECTION_NAME = UserStatus.get_collection_name()
USERS_STATUS_DOC_REF = "userstatus_"
CACHE_TTL = 60 # 60 seconds
class UserStatusCache:
    """Manages user status caching with dynamic invalidation"""
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._timestamps: Dict[str, datetime] = {}

    def get(self, user_uid: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves user status from cache if available and valid.

        Args:
            user_uid (str): The user ID.

        """
        if user_uid in self._cache:
            status_data = self._cache[user_uid]
            # Force refresh for credit-consuming or sensitive operations
            # Check TTL for normal operations
            if datetime.now() - self._timestamps[user_uid] < timedelta(seconds=CACHE_TTL):
                return status_data
            self.invalidate(user_uid)
        return None

    def set(self, user_uid: str, data: Dict[str, Any]) -> None:
        """
        Sets user status data in the cache.

        Args:
            user_uid (str): The user ID.
            data (Dict[str, Any]): The user status data to cache.
        """
        self._cache[user_uid] = data
        self._timestamps[user_uid] = datetime.now()

    def invalidate(self, user_uid: str) -> None:
        """
        Invalidates (removes) user status from the cache.

        Args:
            user_uid (str): The user ID to invalidate.
        """
        self._cache.pop(user_uid, None)
        self._timestamps.pop(user_uid, None)

# Global cache instance
userstatus_cache = UserStatusCache()

# Replace the logger dependency with a standard logger
logger = logging.getLogger(__name__)

async def get_userstatus(
    user_uid: str,
    db: firestore.Client,  # Note: This expects the actual client, not a Depends
    force_fresh: bool = False
) -> tuple[Dict[str, Any], bool]:
    """
    Fetch user status with intelligent caching
    """
    cache_used = False
    if not force_fresh:
        cached_status = userstatus_cache.get(user_uid)
        if cached_status:
            cache_used = True
            return cached_status, cache_used

    try:
        # Get reference to the document
        userstatus_id = USERS_STATUS_DOC_REF + user_uid
        user_ref = db.collection(USERS_STATUS_COLLECTION_NAME).document(userstatus_id)

        # Get the document
        snapshot = user_ref.get()
        if not snapshot.exists:
            raise ResourceNotFoundError(
                resource_type="authorization userstatus",
                resource_id=userstatus_id,
                additional_info={"user_uid": user_uid}
            )

        status_data = snapshot.to_dict()

        # Only cache if not forced fresh
        if not force_fresh:
            userstatus_cache.set(user_uid, status_data)
        return status_data, cache_used

    except ResourceNotFoundError:
        raise
    except Exception as e:
        raise ServiceError(
            operation=f"fetching user status",
            error=e,
            resource_type="userstatus",
            resource_id=user_uid,
            additional_info={
                "force_fresh": force_fresh,
                "collection": USERS_STATUS_COLLECTION_NAME
            }
        ) from e

def _validate_resource_fields(fields: Dict[str, Any]) -> List[str]:
    """
    Filter out invalid fields similar to BaseFirestoreService validation.
    Returns only fields that have actual values to update.
    """
    valid_fields = {
        k: v for k, v in fields.items()
        if v is not None and not (isinstance(v, (list, dict, set)) and len(v) == 0)
    }
    return list(valid_fields.keys())

async def extract_request_fields(request: Request) -> Optional[List[str]]:
    """
    Extract fields from request body for both PATCH and POST methods.
    For GET and DELETE methods, return None as they typically don't have a body.
    """
    # Skip body extraction for GET and DELETE requests
    if request.method.upper() in ["GET", "DELETE", "HEAD", "OPTIONS"]:
        return None

    try:
        body = await request.json()
        if isinstance(body, dict):
            if request.method.upper() == "PATCH":
                return _validate_resource_fields(body)
            if request.method.upper() == "POST":
                # For POST, we want to include all fields being set
                return list(body.keys())
        elif hasattr(body, 'model_dump'):
            data = body.model_dump(exclude_unset=True)
            if request.method.upper() == "PATCH":
                return _validate_resource_fields(data)
            if request.method.upper() == "POST":
                return list(data.keys())

        return None

    except Exception as e:
        logger.warning(f"Could not extract fields from request body: {str(e)}")
        return None  # Return None instead of raising an error

async def authorizeAPIRequest(
    request: Request,
    db: firestore.Client,  # Changed: Now expects actual client instance
    request_resource_fields: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    """
    Authorize API request based on user status and OPA policies.
    Enhanced with credit check information.
    """
    try:
        # Extract fields for both PATCH and POST if not provided
        if not request_resource_fields:
            request_resource_fields = await extract_request_fields(request)

        # Extract request context
        user_uid = request.state.user.get('uid')
        if not user_uid:
            raise AuthorizationError(
                action="access API",
                additional_info={"path": str(request.url)}
            )


        # Determine if we need fresh status
        force_fresh = _should_force_fresh_status(request)
        userstatus, cache_used = await get_userstatus(user_uid, db, force_fresh=force_fresh)

        # Prepare authorization input
        auth_input = {
            "api_url": request.url.path,
            "requestor": {
                "uid": user_uid,
                "usertypes": request.state.user.get("usertypes"),
                "email_verified": request.state.user.get("email_verified"),
                "iam_groups": userstatus.get("iam_groups"),
                "subscriptions": userstatus.get("subscriptions"),
                "sbscrptn_based_insight_credits": userstatus.get("sbscrptn_based_insight_credits"),
                "extra_insight_credits": userstatus.get("extra_insight_credits")
            },
            "method": request.method.lower(),
            "request_resource_fields": request_resource_fields
        }

        ####!!!!!!!!!! OPA call
        # Query OPA
        opa_url = f"{os.getenv('OPA_SERVER_URL', 'http://localhost:8181')}{os.getenv('OPA_DECISION_PATH', '/v1/data/http/authz/ingress/decision')}"
        logger.debug(f"Attempting to connect to OPA at: {opa_url}")
        logger.debug(f"Authorization input: {auth_input}")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    opa_url,
                    json={"input": auth_input},
                    timeout=5.0  # 5 seconds timeout
                )
                logger.debug(f"OPA Response Status: {response.status_code}")
                logger.debug(f"OPA Response Body: {response.text}")
            except httpx.RequestError as e:
                logger.error(f"Failed to connect to OPA: {str(e)}")
                raise ServiceError(
                    operation="API authorization",
                    error=e,
                    resource_type="authorization",
                    additional_info={
                        "opa_url": opa_url,
                        "connection_error": str(e)
                    }
                ) from e
            if response.status_code != 200:
                logger.error(f"OPA authorization failed: {response.text}")
                raise HTTPException(
                    status_code=500,
                    detail="Authorization service error"
                )

            result = response.json()
            if not result.get("result", {}).get("allow", False):
                raise AuthorizationError(
                    action=f"{request.method} {request.url.path}",
                    additional_info={
                        "user_uid": user_uid,
                        "resource_fields": request_resource_fields
                    }
                )

            # Extract credit check information from the OPA response
            credit_check = {}
            if "credit_check" in result.get("result", {}):
                credit_check = result["result"]["credit_check"]

        # More descriptive metadata about the data freshness
        return {
            "used_cached_status": cache_used,
            "required_fresh_status": force_fresh,
            "status_retrieved_at": datetime.now(timezone.utc).isoformat(),
            "credit_check": credit_check
        }

    except (AuthorizationError, ResourceNotFoundError):
        raise
    except Exception as e:
        raise ServiceError(
            operation="API authorization",
            error=e,
            resource_type="authorization",
            additional_info={
                "path": str(request.url),
                "method": request.method,
                "user_uid": request.state.user.get('uid'),
                "resource_fields": request_resource_fields
            }
        ) from e

def _should_force_fresh_status(request: Request) -> bool:
    """
    Determine if we should force a fresh status check based on the request path patterns
    and HTTP methods
    """
    # Path patterns that indicate credit-sensitive operations
    credit_sensitive_patterns = [
        'prediction',
        'user-statuses',
        'historic'
    ]
    # Methods that require fresh status
    sensitive_methods = {'post', 'patch', 'put', 'delete'}

    path = request.url.path.lower()
    method = request.method.lower()

    return (
        any(pattern in path for pattern in credit_sensitive_patterns) or
        method in sensitive_methods
    )
