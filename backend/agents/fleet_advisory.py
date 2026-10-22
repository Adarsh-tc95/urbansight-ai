"""
UrbanSight AI — Agent 4: Fleet Driver In-Cab Advisory Agent
Generates real-time in-cab heads-up advisories, lane merge guidance, and speed reduction alerts for approaching transit vehicles (<300m).
"""

import uuid
from typing import Dict, Any, Optional, Tuple, List
from backend.models import (
    DriverAdvisory, HazardDetection, HazardType, SeverityLevel, BusTelemetry
)
from backend.agents.geospatial_cluster import haversine_distance_meters

MAX_ADVISORY_DISTANCE_METERS: int = 300


class FleetAdvisoryAgent:
    """
    Agent 4: Fleet Driver In-Cab Advisory Engine.
    - Evaluates vehicles approaching hazards within the 300m alert horizon.
    - Computes lane merge recommendations (e.g., "Left lane merge recommended").
    - Computes safe vehicle deceleration speed reduction (e.g., 20 km/h reduction).
    - Categorizes alert severity levels (CRITICAL, WARNING, INFO).
    - Dispatches real-time in-cab HUD telemetry payloads over simulated WebSocket.
    """

    def __init__(self, max_horizon_m: int = MAX_ADVISORY_DISTANCE_METERS):
        self.agent_name = "Agent 4: Fleet Advisory"
        self.max_horizon_m = max_horizon_m

    def compute_alert_level(
        self,
        severity: SeverityLevel,
        distance_meters: int
    ) -> str:
        """
        Calculates driver alert priority level:
        - CRITICAL: immediate threat within 100m or CRITICAL_P1 hazard.
        - WARNING: moderate threat within 100m-250m or HIGH_P2 hazard.
        - INFO: advisory awareness within 250m-300m or MEDIUM_P3/LOW_P4.
        """
        if distance_meters <= 100 or severity == SeverityLevel.CRITICAL_P1:
            return "CRITICAL"
        elif distance_meters <= 250 or severity == SeverityLevel.HIGH_P2:
            return "WARNING"
        else:
            return "INFO"

    def compute_recommendations(
        self,
        hazard_type: HazardType,
        severity: SeverityLevel
    ) -> Tuple[str, int, str]:
        """
        Generates tactical driver guidance:
        Returns: (recommended_lane, speed_reduction_kmh, advice_text)
        """
        if hazard_type == HazardType.POTHOLE:
            lane = "Left lane merge recommended"
            speed_reduction = 20 if severity == SeverityLevel.CRITICAL_P1 else 15
            advice = f"Caution: Deep pothole ahead. {lane}. Reduce speed by {speed_reduction} km/h to prevent axle shock."

        elif hazard_type == HazardType.WATERLOGGING:
            lane = "Center lane merge recommended"
            speed_reduction = 20
            advice = f"Warning: Waterlogged road ahead (hydroplaning risk). {lane}. Reduce speed by {speed_reduction} km/h."

        elif hazard_type == HazardType.ACCIDENT:
            lane = "Extreme left lane merge recommended"
            speed_reduction = 25
            advice = f"Emergency: Vehicle accident ahead. {lane}. Reduce speed by {speed_reduction} km/h and prepare to halt."

        elif hazard_type == HazardType.ROAD_DEBRIS:
            lane = "Right lane merge recommended"
            speed_reduction = 15
            advice = f"Obstacle alert: Debris on carriageway. {lane}. Reduce speed by {speed_reduction} km/h."

        elif hazard_type == HazardType.CONGESTION:
            lane = "Maintain current lane"
            speed_reduction = 15
            advice = f"Traffic bottleneck ahead. {lane}. Reduce speed by {speed_reduction} km/h; expect stop-and-go queue."

        elif hazard_type == HazardType.ROAD_CRACK:
            lane = "Center lane merge recommended"
            speed_reduction = 10
            advice = f"Advisory: Surface cracks ahead. {lane}. Reduce speed by {speed_reduction} km/h."

        else:
            lane = "Proceed with caution"
            speed_reduction = 10
            advice = f"Caution: Road distress reported. {lane}."

        return lane, speed_reduction, advice

    def generate_advisory(
        self,
        hazard: HazardDetection,
        approaching_bus_id: str,
        distance_meters: int = 180,
        advisories_list: Optional[List[DriverAdvisory]] = None
    ) -> DriverAdvisory:
        """
        Generates a DriverAdvisory message and optionally prepends to active advisories list.
        """
        alert_level = self.compute_alert_level(hazard.severity, distance_meters)
        lane, speed_red, advice = self.compute_recommendations(hazard.hazard_type, hazard.severity)

        full_recommendation = (
            f"Caution: {hazard.hazard_type.value} ahead at {hazard.location_name} ({distance_meters}m). "
            f"{lane}. Reduce speed by {speed_red} km/h."
        )

        advisory = DriverAdvisory(
            id=str(uuid.uuid4())[:8],
            bus_id=approaching_bus_id,
            hazard_type=hazard.hazard_type,
            distance_meters=distance_meters,
            recommendation=full_recommendation,
            alert_level=alert_level,
            speed_reduction_kmh=speed_red,
            recommended_lane=lane
        )

        if advisories_list is not None:
            advisories_list.insert(0, advisory)
            if len(advisories_list) > 50:
                advisories_list.pop()

        return advisory

    def evaluate_fleet_proximity(
        self,
        hazard: HazardDetection,
        buses: List[BusTelemetry],
        advisories_list: List[DriverAdvisory]
    ) -> List[DriverAdvisory]:
        """
        Scans all active buses and generates advisories for those within <300m of the hazard.
        """
        generated = []
        for bus in buses:
            dist = haversine_distance_meters(bus.lat, bus.lng, hazard.lat, hazard.lng)
            if dist <= self.max_horizon_m:
                adv = self.generate_advisory(
                    hazard=hazard,
                    approaching_bus_id=bus.bus_id,
                    distance_meters=int(dist),
                    advisories_list=advisories_list
                )
                generated.append(adv)
        return generated
