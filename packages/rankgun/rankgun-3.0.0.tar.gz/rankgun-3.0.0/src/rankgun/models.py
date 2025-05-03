"""Models to define what the API shold return and to ensure type safety."""

from datetime import datetime

from pydantic import BaseModel


class robloxResponse(BaseModel):
    """Expected Roblox Response."""

    path: str
    updateTime: datetime
    user: str
    role: str
