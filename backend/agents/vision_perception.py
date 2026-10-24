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

    def analyze_frame(
        self,
        frame: Any,
        apply_privacy_blur: bool = True
    ) -> Dict[str, Any]:
        """
        Analyzes a single video frame / camera image with OpenCV edge perception:
        1. Validates frame and computes road ROI in lower 65% of frame.
        2. Detects pavement dark anomalies / contours / pothole craters.
        3. Estimates physical depth (cm), contrast, bounding box, and confidence.
        4. Simulates volatile RAM-only DPDP privacy blurring.
        """
        import cv2
        import numpy as np

        if frame is None or not isinstance(frame, np.ndarray):
            return {
                "hazard_detected": False,
                "hazard_type": HazardType.POTHOLE,
                "rdd_code": RDD_CODE_MAPPING[HazardType.POTHOLE],
                "severity": SeverityLevel.LOW_P4,
                "confidence": 0.0,
                "depth_cm": 0.0,
                "contour_area": 0.0,
                "optical_contrast": 0.0,
                "bbox": [0, 0, 100, 100],
                "bounding_box": {"x": 0, "y": 0, "width": 100, "height": 100},
                "normalized_bbox": {"top": "46%", "left": "38%", "width": "30%", "height": "34%"},
                "privacy": self.simulate_dpdp_privacy_redaction()
            }

        h, w = frame.shape[:2]
        frame_area = float(w * h)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if frame.ndim == 3 else frame.copy()

        roi_y_start = int(h * 0.35)
        roi_gray = gray[roi_y_start:, :]
        blurred = cv2.GaussianBlur(roi_gray, (5, 5), 0)
        mean_bg = float(np.mean(blurred))

        if mean_bg < 15.0 or mean_bg > 240.0:
            return {
                "hazard_detected": False,
                "hazard_type": HazardType.POTHOLE,
                "rdd_code": RDD_CODE_MAPPING[HazardType.POTHOLE],
                "severity": SeverityLevel.LOW_P4,
                "confidence": 0.0,
                "depth_cm": 0.0,
                "contour_area": 0.0,
                "optical_contrast": 0.0,
                "bbox": [0, 0, w, h],
                "bounding_box": {"x": 0, "y": 0, "width": w, "height": h},
                "normalized_bbox": {"top": "46%", "left": "38%", "width": "30%", "height": "34%"},
                "privacy": self.simulate_dpdp_privacy_redaction()
            }

        _, thresh = cv2.threshold(blurred, 65, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best_contour = None
        max_area = 0.0
        for c in contours:
            area = float(cv2.contourArea(c))
            if area > max_area and area >= 80:
                max_area = area
                best_contour = c

        if best_contour is not None:
            bx, by, bw, bh = cv2.boundingRect(best_contour)
            by += roi_y_start

            aspect_ratio = round(float(bw) / max(1.0, float(bh)), 2)
            if aspect_ratio >= 2.8 or aspect_ratio <= 0.35:
                h_type = HazardType.ROAD_CRACK
                rdd_code = "D00 (Longitudinal Crack)" if aspect_ratio >= 2.8 else "D10 (Transverse Crack)"
            else:
                h_type = HazardType.POTHOLE
                rdd_code = RDD_CODE_MAPPING[HazardType.POTHOLE]

            mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.drawContours(mask, [best_contour + [0, roi_y_start]], -1, 255, -1)
            mean_contour = float(cv2.mean(gray, mask=mask)[0])
            contrast_diff = max(0.0, mean_bg - mean_contour)

            depth_cm = min(25.0, round(4.0 + (max_area / frame_area) * 85.0 + contrast_diff * 0.15, 1))
            if depth_cm >= 8.0:
                sev = SeverityLevel.CRITICAL_P1
            elif depth_cm >= 5.0:
                sev = SeverityLevel.HIGH_P2
            elif depth_cm >= 3.0:
                sev = SeverityLevel.MEDIUM_P3
            else:
                sev = SeverityLevel.LOW_P4

            conf = min(0.99, max(0.72, round(0.75 + (contrast_diff / 100.0) * 0.20 + (max_area / frame_area) * 2.0, 3)))

            top_pct = f"{round((by / h) * 100, 1)}%"
            left_pct = f"{round((bx / w) * 100, 1)}%"
            width_pct = f"{round((bw / w) * 100, 1)}%"
            height_pct = f"{round((bh / h) * 100, 1)}%"

            return {
                "hazard_detected": True,
                "hazard_type": h_type,
                "rdd_code": rdd_code,
                "aspect_ratio": aspect_ratio,
                "severity": sev,
                "confidence": conf,
                "depth_cm": depth_cm,
                "contour_area": max_area,
                "optical_contrast": round(contrast_diff, 2),
                "bbox": [bx, by, bw, bh],
                "bounding_box": {"x": bx, "y": by, "width": bw, "height": bh},
                "normalized_bbox": {"top": top_pct, "left": left_pct, "width": width_pct, "height": height_pct},
                "privacy": self.simulate_dpdp_privacy_redaction()
            }

        return {
            "hazard_detected": False,
            "hazard_type": HazardType.POTHOLE,
            "rdd_code": RDD_CODE_MAPPING[HazardType.POTHOLE],
            "severity": SeverityLevel.LOW_P4,
            "confidence": 0.50,
            "depth_cm": 2.0,
            "contour_area": 0.0,
            "optical_contrast": 0.0,
            "bbox": [int(w * 0.38), int(h * 0.46), int(w * 0.30), int(h * 0.34)],
            "bounding_box": {"x": int(w * 0.38), "y": int(h * 0.46), "width": int(w * 0.30), "height": int(h * 0.34)},
            "normalized_bbox": {"top": "46%", "left": "38%", "width": "30%", "height": "34%"},
            "privacy": self.simulate_dpdp_privacy_redaction()
        }

    def draw_detections(self, frame: Any, analysis: Dict[str, Any]) -> Any:
        """Draws bounding box, defect type, and depth watermark onto frame."""
        import cv2
        import numpy as np
        if frame is None or not isinstance(frame, np.ndarray):
            return frame
        out = frame.copy()
        if not analysis.get("hazard_detected"):
            return out
        bbox = analysis.get("bounding_box") or {}
        x = int(bbox.get("x", 0))
        y = int(bbox.get("y", 0))
        w = int(bbox.get("width", 50))
        h = int(bbox.get("height", 50))
        color = (0, 0, 255)
        cv2.rectangle(out, (x, y), (x + w, y + h), color, 2)
        label = f"{analysis.get('rdd_code', 'DEFECT')} | {analysis.get('depth_cm', 0)}cm"
        cv2.putText(out, label, (x, max(15, y - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
        return out

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
