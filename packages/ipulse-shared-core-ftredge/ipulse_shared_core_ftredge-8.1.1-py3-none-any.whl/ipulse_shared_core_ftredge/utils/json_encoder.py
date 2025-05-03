import json
from datetime import datetime
from google.cloud.firestore_v1._helpers import DatetimeWithNanoseconds
from google.api_core import datetime_helpers

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles Firestore datetime types."""
    def default(self, obj):
        if isinstance(obj, (datetime, DatetimeWithNanoseconds)):
            return obj.isoformat()
        if isinstance(obj, datetime_helpers.DatetimeWithNanoseconds):
            return obj.isoformat()
        return super().default(obj)
