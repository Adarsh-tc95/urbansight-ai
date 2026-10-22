"""
UrbanSight AI — Agent 1: Vision Perception Engine
Edge-native simulated inference pipeline (YOLOv8/v10, RDD2022 damage codes, DPDP Act 2023 privacy redaction).
"""

from typing import Dict, Any, Optional, Tuple, List
import uuid
from backend.models import HazardType, SeverityLevel


# Standard RDD2020 / RDD2022 international road distress classification codes
RDD_CODE_MAPPING: Dict[HazardType, str] = {
    HazardType.POTHOLE: "D40 (Pothole / Subsidence)",
    HazardType.ROAD_CRACK: "D00/D10/D20 (Longitudinal / Transverse / Alligator Fatigue Cracks)",
    HazardType.WATERLOGGING: "W01 (Puddle & Monsoon Waterlogging / Hydroplaning Risk)",
    HazardType.CONGESTION: "T10 (High Pavement Density Bottleneck)",
    HazardType.ROAD_DEBRIS: "X90 (Carriageway Obstacle / Foreign Debris)",
    HazardType.ACCIDENT: "A01 (Emergency Vehicle Collision / Road Obstruction)"
}

CONFIDENCE_THRESHOLD_DEFAULT: float = 0.70


class LowConfidenceError(ValueError):
    """Raised when edge visual detection confidence is below the operational threshold."""
    pass


class VisionPerceptionAgent:
    """
    Agent 1: Vision Perception Engine.
    Simulates on-device camera inference (YOLOv8/v10 + SegFormer-B0) with:
    - Defect category verification and RDD2022 code tagging.
    - Zero-persistence in-memory DPDP Act 2023 privacy redaction (YuNet face & plate mask).
    - Confidence threshold gating (>= 0.70).
    - Pavement physical distress metric estimation (depth, length, area, severity).
    """

    def __init__(self, min_confidence: float = CONFIDENCE_THRESHOLD_DEFAULT):
        self.agent_name = "Agent 1: Vision Perception"
        self.min_confidence = min_confidence
        self.fps = 30.0
        self.model_engine = "YOLOv10s-ORDDC24 (INT8 Quantized / TensorRT 10.x)"
        self.privacy_engine = "YuNet + YOLOv8n-Plate (DPDP Act 2023 §2(t))"
        self.redaction_count = 0

    def validate_confidence(self, confidence: float) -> bool:
        """Validates that edge detection meets or exceeds the operational threshold."""
        return confidence >= self.min_confidence

    def simulate_dpdp_privacy_redaction(
        self,
        frame_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Simulates volatile RAM-only redaction compliant with Digital Personal Data Protection
        (DPDP) Act 2023 Section 2(t) & GDPR Recital 26.
        Applies solid-fill zero-entropy mask and Gaussian blur (sigma >= 35) over detected
        faces (OpenCV YuNet) and license plates (YOLOv8n-Plate).
        Raw unblurred frame buffer is immediately discarded with zero persistent storage.
        """
        self.redaction_count += 1
        return {
            "dpdp_compliant": True,
            "section": "DPDP Act 2023 §2(t)",
            "faces_masked": 2,
            "plates_masked": 1,
            "obfuscation_type": "ZERO_ENTROPY_SOLID_FILL_GAUSSIAN_BLUR_SIGMA_35",
            "zero_storage_persistence": True,
            "volatile_ram_discarded": True,
            "audit_token": f"DPDP-AUDIT-{uuid.uuid4().hex[:8].upper()}"
        }

    def estimate_physical_distress(
        self,
        hazard_type: HazardType,
        damage_depth_cm: Optional[float] = None,
        affected_length_m: Optional[float] = None,
        estimated_area_sqm: Optional[float] = None
    ) -> Tuple[SeverityLevel, Dict[str, Optional[float]]]:
        """
        Estimates pavement physical distress metrics (depth, length, area)
        and classifies actionable SeverityLevel (CRITICAL_P1, HIGH_P2, MEDIUM_P3, LOW_P4).
        """
        depth = damage_depth_cm
        length = affected_length_m
        area = estimated_area_sqm

        if hazard_type == HazardType.POTHOLE:
            if depth is None:
                depth = 8.5  # Typical detected pothole depth
            if area is None:
                # Area roughly pi * (diameter / 2)^2
                area = round(0.4 + (depth / 10.0) * 0.8, 2)
            if length is None:
                length = round((area ** 0.5) * 1.2, 2)

            if depth >= 8.0 or (area and area >= 1.5):
                severity = SeverityLevel.CRITICAL_P1
            elif depth >= 4.0:
                severity = SeverityLevel.HIGH_P2
            else:
                severity = SeverityLevel.MEDIUM_P3

        elif hazard_type == HazardType.ROAD_CRACK:
            if depth is None:
                depth = 2.5
            if length is None:
                length = 12.0
            if area is None:
                area = round(length * 0.15, 2)

            if length >= 20.0 or depth >= 4.0:
                severity = SeverityLevel.HIGH_P2
            elif length >= 8.0:
                severity = SeverityLevel.MEDIUM_P3
            else:
                severity = SeverityLevel.LOW_P4

        elif hazard_type == HazardType.WATERLOGGING:
            depth = None
            if length is None:
                length = 30.0
            if area is None:
                area = round(length * 3.5, 2)

            if length >= 25.0 or (area and area >= 80.0):
                severity = SeverityLevel.HIGH_P2
            else:
                severity = SeverityLevel.MEDIUM_P3

        elif hazard_type == HazardType.ACCIDENT:
            severity = SeverityLevel.CRITICAL_P1
            if length is None:
                length = 15.0
            if area is None:
                area = 45.0

        elif hazard_type == HazardType.ROAD_DEBRIS:
            severity = SeverityLevel.HIGH_P2
            if length is None:
                length = 3.0
            if area is None:
                area = 2.5

        elif hazard_type == HazardType.CONGESTION:
            severity = SeverityLevel.MEDIUM_P3
            if length is None:
                length = 300.0
            if area is None:
                area = round(length * 7.0, 2)

        else:
            severity = SeverityLevel.MEDIUM_P3

        metrics = {
            "depth_cm": depth,
            "length_m": length,
            "area_sqm": area
        }
        return severity, metrics

    def detect(
        self,
        bus_id: str,
        hazard_type: HazardType,
        lat: float,
        lng: float,
        location_name: str,
        confidence: float = 0.95,
        damage_depth_cm: Optional[float] = None,
        affected_length_m: Optional[float] = None,
        estimated_area_sqm: Optional[float] = None,
        enable_dpdp: bool = True
    ) -> Dict[str, Any]:
        """
        Executes end-to-end edge vision inference simulation:
        1. Validates confidence threshold (>= 0.70).
        2. Applies DPDP Act 2023 zero-persistence in-memory privacy redaction.
        3. Estimates physical distress dimensions and assigns severity level.
        4. Attaches RDD2022 standardized defect code.
        """
        if not self.validate_confidence(confidence):
            raise LowConfidenceError(
                f"Edge detection confidence {confidence:.2f} is below the operational threshold {self.min_confidence:.2f}"
            )

        privacy_info = self.simulate_dpdp_privacy_redaction() if enable_dpdp else {
            "dpdp_compliant": False,
            "warning": "PRIVACY_BLUR_DISABLED"
        }

        severity, distress = self.estimate_physical_distress(
            hazard_type=hazard_type,
            damage_depth_cm=damage_depth_cm,
            affected_length_m=affected_length_m,
            estimated_area_sqm=estimated_area_sqm
        )

        rdd_code = RDD_CODE_MAPPING.get(hazard_type, "UNKNOWN")

        return {
            "bus_id": bus_id,
            "hazard_type": hazard_type,
            "rdd_code": rdd_code,
            "severity": severity,
            "confidence": confidence,
            "lat": lat,
            "lng": lng,
            "location_name": location_name,
            "damage_depth_cm": distress["depth_cm"],
            "affected_length_m": distress["length_m"],
            "estimated_area_sqm": distress["area_sqm"],
            "privacy": privacy_info,
            "model_metadata": {
                "engine": self.model_engine,
                "fps": self.fps,
                "payload_size_kb": 11.8
            }
        }
