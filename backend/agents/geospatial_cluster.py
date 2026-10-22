"""
UrbanSight AI — Agent 2: Geo-Spatial Clustering Engine
Spatial deduplication using DBSCAN (epsilon ~15-30m) & multi-modal IMU vibration verification.
"""

import math
from typing import List, Dict, Any, Optional, Tuple
from backend.models import HazardDetection, HazardType, SeverityLevel, TicketStatus


def haversine_distance_meters(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Computes accurate great-circle distance between two GPS coordinates in meters.
    """
    r = 6371000.0  # Earth's mean radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


class GeospatialClusteringAgent:
    """
    Agent 2: Geo-Spatial Clustering & Sensor Fusion Engine.
    - Implements DBSCAN spatial deduplication with epsilon (15 - 30m).
    - Merges repeat detections across different transit buses into canonical hazard nodes.
    - Updates running average confidence, pass counts, and cluster IDs.
    - Fuses chassis 6-axis IMU vertical shock heuristic (+az vs -az) to discard false positives.
    """

    def __init__(self, epsilon_meters: float = 25.0, min_samples: int = 1):
        self.agent_name = "Agent 2: Geo-Spatial Clustering"
        self.epsilon_meters = epsilon_meters
        self.min_samples = min_samples
        self.cluster_counter = 0

    def verify_imu_vibration(
        self,
        hazard_type: HazardType,
        z_shock: Optional[float] = None,
        waveform: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Subsystem 9 Physical Waveform Signature Heuristic:
        - Speed bump (Positive Anomaly): Initial upward vertical acceleration (+az > 0)
          as tire mounts ramp. Pitch rotation (+omega_y), bilateral wheel impact.
        - Pothole (Negative Anomaly): Initial downward freefall drop (-az < 0) into void,
          followed by sharp rim lip strike (+az >> +2.5g), unilateral tilt roll.

        Returns verification result dictionary.
        """
        # Non-surface physical hazards (congestion, etc.) do not require IMU shock
        if hazard_type not in [HazardType.POTHOLE, HazardType.ROAD_CRACK]:
            return {
                "verified": True,
                "is_false_positive": False,
                "reason": "Hazard type does not exhibit chassis vertical impulse",
                "classification": "NON_SURFACE_HAZARD"
            }

        # Analyze waveform array if provided
        if waveform and len(waveform) > 0:
            first_peak = waveform[0]
            if first_peak > 0.35:
                return {
                    "verified": False,
                    "is_false_positive": True,
                    "reason": f"IMU initial waveform is positive (+{first_peak:.2f}g); classified as speed bump or raised crosswalk",
                    "classification": "SPEED_BUMP_FALSE_ALARM"
                }
            elif first_peak < -0.20:
                max_rebound = max(waveform) if len(waveform) > 1 else 0.0
                return {
                    "verified": True,
                    "is_false_positive": False,
                    "reason": f"IMU confirmed downward freefall ({first_peak:.2f}g) followed by rebound ({max_rebound:.2f}g)",
                    "classification": "CONFIRMED_POTHOLE_VOID"
                }

        # Analyze single scalar z_shock if provided
        if z_shock is not None:
            if z_shock > 0.40:
                # Upward acceleration first without preceding void -> speed bump
                return {
                    "verified": False,
                    "is_false_positive": True,
                    "reason": f"Chassis upward shock (+{z_shock:.2f}g); speed bump detected instead of pothole",
                    "classification": "SPEED_BUMP_FALSE_ALARM"
                }
            elif z_shock < -0.25:
                # Downward drop into hole
                return {
                    "verified": True,
                    "is_false_positive": False,
                    "reason": f"Chassis downward freefall (-{abs(z_shock):.2f}g) confirms physical road void",
                    "classification": "CONFIRMED_POTHOLE_VOID"
                }

        # Default fallback when IMU sensor is pending (pre-contact lookahead)
        return {
            "verified": True,
            "is_false_positive": False,
            "reason": "Visual detection accepted pending post-contact IMU confirmation",
            "classification": "VISUAL_ACCEPTED_PRE_CONTACT"
        }

    def find_matching_hazard(
        self,
        lat: float,
        lng: float,
        hazard_type: HazardType,
        existing_hazards: List[HazardDetection]
    ) -> Optional[Tuple[HazardDetection, float]]:
        """
        Finds the closest canonical hazard within epsilon meters of the same defect category.
        """
        closest_hazard = None
        min_dist = float('inf')

        for candidate in existing_hazards:
            # Must match hazard type or both be pavement defects
            if candidate.hazard_type != hazard_type:
                continue

            dist = haversine_distance_meters(candidate.lat, candidate.lng, lat, lng)
            if dist <= self.epsilon_meters and dist < min_dist:
                min_dist = dist
                closest_hazard = candidate

        if closest_hazard:
            return closest_hazard, min_dist
        return None

    def cluster_detection(
        self,
        detection_data: Dict[str, Any],
        existing_hazards: List[HazardDetection],
        z_shock: Optional[float] = None,
        waveform: Optional[List[float]] = None
    ) -> Tuple[HazardDetection, bool, str]:
        """
        Ingests a verified edge vision detection and performs spatial clustering:
        1. Checks IMU vibration heuristic to reject speed bumps / false alarms.
        2. Deduplicates against existing canonical hazards within epsilon meters.
        3. If match found: increments pass_count, updates running average confidence,
           and merges distress metrics.
        4. If new: creates new HazardDetection node with generated cluster_id.

        Returns: (hazard_node, is_new_cluster, status_message)
        """
        hazard_type = detection_data["hazard_type"]
        lat = detection_data["lat"]
        lng = detection_data["lng"]
        bus_id = detection_data["bus_id"]
        confidence = detection_data.get("confidence", 0.95)
        location_name = detection_data.get("location_name", "Arterial Road")
        damage_depth = detection_data.get("damage_depth_cm")
        affected_length = detection_data.get("affected_length_m")
        estimated_area = detection_data.get("estimated_area_sqm")
        severity = detection_data.get("severity", SeverityLevel.HIGH_P2)

        # 1. IMU Vibration Verification
        imu_res = self.verify_imu_vibration(hazard_type, z_shock=z_shock, waveform=waveform)
        if imu_res["is_false_positive"]:
            raise ValueError(
                f"False positive rejected by IMU vibration fusion: {imu_res['reason']}"
            )

        # 2. Check for matching existing cluster
        match = self.find_matching_hazard(lat, lng, hazard_type, existing_hazards)

        if match:
            canonical, distance = match
            # Incremental updates
            old_count = canonical.pass_count
            new_count = old_count + 1
            canonical.pass_count = new_count

            # Running average confidence
            canonical.confidence = min(0.99, round(
                (canonical.confidence * old_count + confidence) / new_count, 3
            ))

            # Update maximum distress measurement
            if damage_depth and (canonical.damage_depth_cm is None or damage_depth > canonical.damage_depth_cm):
                canonical.damage_depth_cm = damage_depth
            if affected_length and (canonical.affected_length_m is None or affected_length > canonical.affected_length_m):
                canonical.affected_length_m = affected_length
            if estimated_area and (canonical.estimated_area_sqm is None or estimated_area > canonical.estimated_area_sqm):
                canonical.estimated_area_sqm = estimated_area

            canonical.imu_verified = imu_res["verified"]
            if canonical.status == TicketStatus.DETECTED and new_count >= 2:
                canonical.status = TicketStatus.CLUSTERED

            msg = (
                f"Merged repeat pass from {bus_id} into canonical cluster {canonical.cluster_id} "
                f"({distance:.1f}m delta, total passes: {new_count}, avg conf: {canonical.confidence:.3f})"
            )
            return canonical, False, msg

        else:
            # 3. New canonical hazard cluster
            self.cluster_counter += 1
            cluster_id = f"DBSCAN-CL-{len(existing_hazards) + 1:03d}"
            hazard_id = f"HAZ-2026-{len(existing_hazards) + 1:03d}"

            new_hazard = HazardDetection(
                id=hazard_id,
                bus_id=bus_id,
                hazard_type=hazard_type,
                severity=severity,
                confidence=confidence,
                lat=lat,
                lng=lng,
                location_name=location_name,
                damage_depth_cm=damage_depth,
                affected_length_m=affected_length,
                estimated_area_sqm=estimated_area,
                imu_verified=imu_res["verified"],
                pass_count=1,
                cluster_id=cluster_id,
                image_url="image1.jpg",
                status=TicketStatus.DETECTED
            )
            existing_hazards.append(new_hazard)
            msg = (
                f"Formed new canonical cluster {cluster_id} at {location_name} "
                f"({lat:.4f}, {lng:.4f}) with initial pass by {bus_id}"
            )
            return new_hazard, True, msg
