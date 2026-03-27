from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class AuthEvent(BaseModel):
    event_id: str = Field(..., description="Unique event id")
    user_id: str = Field(..., description="Unique user id")
    timestamp: datetime = Field(..., description="Event timestamp in ISO format")
    ip_address: Optional[str] = Field(None, description="Source IP address")
    latitude: Optional[float] = Field(None, description="Approximate geo latitude")
    longitude: Optional[float] = Field(None, description="Approximate geo longitude")
    location: Optional[str] = Field(None, description="City/Region if available")
    user_agent: Optional[str] = Field(None, description="User agent string")
    device_id: Optional[str] = Field(None, description="Device identifier if available")
    resource: str = Field(..., description="Resource accessed (app/service)")
    action: str = Field(..., description="login/access/logout/authorize/etc.")
    success: bool = Field(..., description="True if successful")
    mfa_used: Optional[bool] = Field(None, description="Whether MFA was used")
    failure_reason: Optional[str] = Field(None, description="Reason if failed")
    privilege_level: Optional[str] = Field(None, description="e.g., user/admin/svc")


class IngestResponse(BaseModel):
    accepted: int
    errors: List[str] = []


class Anomaly(BaseModel):
    event_id: str
    user_id: str
    timestamp: datetime
    score: float
    risk: float
    reasons: List[str]
    feature_contributions: dict


class Alert(BaseModel):
    alert_id: str
    event_id: str
    user_id: str
    risk: float
    created_at: datetime
    channel: str
    payload: dict


class UserProfile(BaseModel):
    user_id: str
    typical_hours: List[int]
    typical_locations: List[str]
    failure_rate: float
    resource_frequency: dict
