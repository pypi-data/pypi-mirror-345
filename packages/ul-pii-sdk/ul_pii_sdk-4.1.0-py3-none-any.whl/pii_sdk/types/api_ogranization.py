from enum import Enum
from typing import Any, Dict, List, Optional

from pytz import all_timezones
from ul_api_utils.api_resource.api_response_payload_alias import ApiBaseUserModelPayloadResponse
from pydantic import BaseModel


TimeZonesEnum = Enum('tz_type', {tz_name.lower().replace('/', '_'): tz_name for tz_name in all_timezones})       # type: ignore


class ApiOrganizationData(BaseModel):
    admin_notes: Optional[str] = None
    name: str
    available_permissions: List[int]
    timezones: List[TimeZonesEnum]


class ApiOrganization(ApiBaseUserModelPayloadResponse):
    admin_notes: Optional[str] = None
    organization_data: ApiOrganizationData
    frontend_settings: Dict[str, Any]
    teams_count: int
    users_count: int
