from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class HazardType(str, Enum):
    POTHOLE = "POTHOLE"
    ROAD_CRACK = "ROAD_CRACK"
    WATERLOGGING = "WATERLOGGING"
    CONGESTION = "CONGESTION"
    ROAD_DEBRIS = "ROAD_DEBRIS"
    ACCIDENT = "ACCIDENT"

class SeverityLevel(str, Enum):
    CRITICAL_P1 = "CRITICAL_P1"
    HIGH_P2 = "HIGH_P2"
    MEDIUM_P3 = "MEDIUM_P3"
    LOW_P4 = "LOW_P4"

class TicketStatus(str, Enum):
    DETECTED = "DETECTED"
    CLUSTERED = "CLUSTERED"
    AUTO_DISPATCHED = "AUTO_DISPATCHED"
    CREW_ASSIGNED = "CREW_ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"

class BusTelemetry(BaseModel):
    bus_id: str
    route_name: str
    lat: float
    lng: float
    speed_kmh: float
    heading_deg: float
    camera_status: str = "ONLINE_30FPS"
    privacy_blur_active: bool = True
    last_ping: str = Field(default_factory=lambda: datetime.now().isoformat())

class HazardDetection(BaseModel):
    id: str
    bus_id: str
    hazard_type: HazardType
    severity: SeverityLevel
    confidence: float  # e.g., 0.96
    lat: float
    lng: float
    location_name: str
    damage_depth_cm: Optional[float] = None
    affected_length_m: Optional[float] = None
    estimated_area_sqm: Optional[float] = None
    imu_verified: Optional[bool] = None
    pass_count: int = 1
    cluster_id: Optional[str] = None
    image_url: Optional[str] = None
    status: TicketStatus = TicketStatus.DETECTED
    pwd_ticket_id: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class PWDWorkOrder(BaseModel):
    ticket_id: str
    hazard_id: str
    hazard_type: HazardType
    severity: SeverityLevel
    location_name: str
    lat: float
    lng: float
    cluster_count: int
    sla_hours: int = 48
    dispatched_to: str = "BBMP Ward 142 / PWD Division 4"
    status: TicketStatus = TicketStatus.AUTO_DISPATCHED
    cpwd_sor_code: Optional[str] = None
    repair_methodology: Optional[str] = None
    estimated_cost_inr: Optional[float] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class DriverAdvisory(BaseModel):
    id: str
    bus_id: str
    hazard_type: HazardType
    distance_meters: int
    recommendation: str
    alert_level: str = "WARNING"
    speed_reduction_kmh: Optional[int] = None
    recommended_lane: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class AgentEventLog(BaseModel):
    id: str
    agent_name: str  # "Agent 1: Vision", "Agent 2: DBSCAN", "Agent 3: PWD Dispatch", "Agent 4: Fleet Advisory"
    action: str
    detail: str
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))
