"""
UrbanSight AI — E2E Test Suite Helpers & Reference Engines
Provides high-fidelity mathematical, geospatial, OpenCV, and ISO 6709 reference
utilities for opaque-box testing of all 17 UrbanSight AI platform features.
"""

import math
import struct
import io
import re
import json
import uuid
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timezone
import cv2
import numpy as np
from PIL import Image
from PIL.TiffImagePlugin import IFDRational

# =============================================================================
# 1. ISO 6709 QuickTime & JPEG EXIF GPS Generators & Parsers (Feature 6)
# =============================================================================

def format_iso6709(lat: float, lng: float, alt: Optional[float] = None) -> str:
    """Formats decimal coordinates into ISO 6709 standard string representation."""
    lat_sign = "+" if lat >= 0 else "-"
    lng_sign = "+" if lng >= 0 else "-"
    lat_str = f"{lat_sign}{abs(lat):07.4f}"
    lng_str = f"{lng_sign}{abs(lng):08.4f}"
    if alt is not None:
        alt_sign = "+" if alt >= 0 else "-"
        return f"{lat_str}{lng_str}{alt_sign}{abs(alt):.1f}/"
    return f"{lat_str}{lng_str}/"

def parse_iso6709(coord_str: str) -> Optional[Tuple[float, float, Optional[float]]]:
    """Extracts latitude, longitude, and optional altitude from ISO 6709 string."""
    pattern = r'([+-]\d+(?:\.\d+)?)([+-]\d+(?:\.\d+)?)(?:([+-]\d+(?:\.\d+)?))?/'
    match = re.search(pattern, coord_str)
    if match:
        lat = float(match.group(1))
        lng = float(match.group(2))
        alt = float(match.group(3)) if match.group(3) else None
        return lat, lng, alt
    return None

def build_mp4_with_location_atom(lat: float, lng: float, alt: Optional[float] = None) -> bytes:
    """
    Constructs a synthetic yet fully valid MP4 byte stream containing
    an ISO 6709 location atom (b'\\xa9xyz') inside a 'udta' (user data) box.
    """
    coord_text = format_iso6709(lat, lng, alt).encode('utf-8')
    atom_data_len = len(coord_text)
    atom_size = 4 + 4 + 2 + 2 + atom_data_len
    atom_bytes = struct.pack(">I4sHH", atom_size, b'\xa9xyz', atom_data_len, 0x55C4) + coord_text

    udta_size = 8 + len(atom_bytes)
    udta_bytes = struct.pack(">I4s", udta_size, b'udta') + atom_bytes

    moov_size = 8 + len(udta_bytes)
    moov_bytes = struct.pack(">I4s", moov_size, b'moov') + udta_bytes

    ftyp_payload = b'mp42\x00\x00\x00\x00mp42isom'
    ftyp_size = 8 + len(ftyp_payload)
    ftyp_bytes = struct.pack(">I4s", ftyp_size, b'ftyp') + ftyp_payload

    return ftyp_bytes + moov_bytes

def parse_mp4_quicktime_gps(file_bytes: bytes) -> Optional[Dict[str, Any]]:
    """Zero-dependency pure-Python MP4 / QuickTime ISO 6709 GPS atom extractor."""
    target = b'\xa9xyz'
    idx = 0
    while True:
        pos = file_bytes.find(target, idx)
        if pos == -1:
            break
        chunk = file_bytes[pos + 4: pos + 64]
        try:
            text = chunk.decode('utf-8', errors='ignore')
            coords = parse_iso6709(text)
            if coords:
                return {
                    "source": "QUICKTIME_EXIF_XYZ",
                    "lat": coords[0],
                    "lng": coords[1],
                    "altitude_m": coords[2]
                }
        except Exception:
            pass
        idx = pos + 4
    return None

def build_jpeg_with_exif_gps(lat: float, lng: float, alt: float = 850.0) -> bytes:
    """Constructs a valid JPEG image with embedded EXIF GPS IFD metadata (Tag 34853)."""
    img = Image.new('RGB', (100, 100), color=(128, 128, 128))
    
    def deg_to_dms_rational(deg_float: float):
        deg = int(abs(deg_float))
        min_f = (abs(deg_float) - deg) * 60
        minute = int(min_f)
        sec = round((min_f - minute) * 60, 4)
        return (
            IFDRational(deg, 1),
            IFDRational(minute, 1),
            IFDRational(int(sec * 10000), 10000)
        )

    lat_ref = 'N' if lat >= 0 else 'S'
    lng_ref = 'E' if lng >= 0 else 'W'
    lat_dms = deg_to_dms_rational(lat)
    lng_dms = deg_to_dms_rational(lng)

    exif = img.getexif()
    gps_ifd = exif.get_ifd(0x8825)
    gps_ifd[1] = lat_ref
    gps_ifd[2] = lat_dms
    gps_ifd[3] = lng_ref
    gps_ifd[4] = lng_dms
    gps_ifd[6] = IFDRational(int(alt * 10), 10)

    buf = io.BytesIO()
    img.save(buf, format='JPEG', exif=exif)
    return buf.getvalue()

def parse_jpeg_exif_gps(file_bytes: bytes) -> Optional[Dict[str, Any]]:
    """Extracts GPS coordinates from JPEG EXIF IFD Tag 34853."""
    try:
        img = Image.open(io.BytesIO(file_bytes))
        exif = img.getexif()
        if not exif:
            return None
        gps_ifd = exif.get_ifd(0x8825)
        if not gps_ifd:
            return None

        def rational_to_float(r):
            if isinstance(r, tuple) and len(r) == 2:
                return float(r[0]) / float(r[1]) if r[1] != 0 else 0.0
            return float(r)

        lat_dms = gps_ifd.get(2)
        lat_ref = gps_ifd.get(1, 'N')
        lng_dms = gps_ifd.get(4)
        lng_ref = gps_ifd.get(3, 'E')

        if not lat_dms or not lng_dms:
            return None

        d = rational_to_float(lat_dms[0])
        m = rational_to_float(lat_dms[1])
        s = rational_to_float(lat_dms[2])
        lat = d + m / 60.0 + s / 3600.0
        if lat_ref.upper() == 'S':
            lat = -lat

        d = rational_to_float(lng_dms[0])
        m = rational_to_float(lng_dms[1])
        s = rational_to_float(lng_dms[2])
        lng = d + m / 60.0 + s / 3600.0
        if lng_ref.upper() == 'W':
            lng = -lng

        alt_val = gps_ifd.get(6)
        alt = rational_to_float(alt_val) if alt_val else None

        return {
            "source": "JPEG_EXIF_GPS",
            "lat": round(lat, 6),
            "lng": round(lng, 6),
            "altitude_m": round(alt, 1) if alt is not None else None
        }
    except Exception:
        return None

# =============================================================================
# 2. Edge Computer Vision & Physical Depth Reference Engine (Features 3, 4, 5)
# =============================================================================

def generate_synthetic_road_frame(
    width: int = 640,
    height: int = 480,
    defect_type: str = "POTHOLE",
    defect_pos: Tuple[int, int] = (300, 320),
    defect_size: Tuple[int, int] = (60, 40),
    add_face_plate: bool = False
) -> np.ndarray:
    """
    Generates a realistic asphalt road image frame with asphalt texture,
    road markings, and an optical distress defect for CV algorithm verification.
    """
    rng = np.random.RandomState(42)
    base = rng.normal(120, 12, (height, width)).clip(0, 255).astype(np.uint8)
    frame = cv2.cvtColor(base, cv2.COLOR_GRAY2BGR)

    cv2.line(frame, (width // 2, height // 3), (width // 4, height), (240, 240, 240), 4)

    cx, cy = defect_pos
    w, h = defect_size

    if defect_type == "POTHOLE":
        cv2.ellipse(frame, (cx, cy), (w // 2, h // 2), 15, 0, 360, (25, 25, 25), -1)
        cv2.ellipse(frame, (cx - 2, cy - 2), (w // 3, h // 3), 15, 0, 360, (10, 10, 10), -1)
    elif defect_type == "ROAD_CRACK":
        pts = np.array([
            [cx - w // 2, cy - h // 2],
            [cx - w // 4, cy - h // 4 + 4],
            [cx, cy - 2],
            [cx + w // 4, cy + h // 4 - 3],
            [cx + w // 2, cy + h // 2]
        ], np.int32)
        cv2.polylines(frame, [pts], isClosed=False, color=(15, 15, 15), thickness=3)
    elif defect_type == "WATERLOGGING":
        cv2.ellipse(frame, (cx, cy), (w, h // 2), 0, 0, 360, (70, 85, 95), -1)

    if add_face_plate:
        cv2.circle(frame, (120, 80), 22, (180, 160, 140), -1)
        cv2.rectangle(frame, (width - 150, 220), (width - 80, 250), (230, 230, 230), -1)
        cv2.putText(frame, "KA-09-EA-102", (width - 145, 242), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 0), 1)

    return frame

class EdgeCVPerceptionAnalyzer:
    """Reference Edge CV Pipeline."""

    def __init__(self, min_confidence: float = 0.70):
        self.min_confidence = min_confidence

    def analyze_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        h, w = frame.shape[:2]
        frame_area = float(w * h)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        roi_y_start = int(h * 0.35)
        roi_gray = gray[roi_y_start:, :]
        
        blurred = cv2.GaussianBlur(roi_gray, (5, 5), 0)
        mean_bg = float(np.mean(blurred))

        # Illumination quality gating: pure black / total glare cannot produce reliable road detections
        if mean_bg < 15.0 or mean_bg > 240.0:
            return {
                "frame_width": w,
                "frame_height": h,
                "detections_count": 0,
                "detections": []
            }

        _, thresh = cv2.threshold(blurred, 65, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections = []
        for c in contours:
            area = cv2.contourArea(c)
            if area < 80:
                continue
            
            bx, by, bw, bh = cv2.boundingRect(c)
            by += roi_y_start

            mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.drawContours(mask, [c + [0, roi_y_start]], -1, 255, -1)
            mean_contour = float(cv2.mean(gray, mask=mask)[0])

            contrast_diff = max(0.0, mean_bg - mean_contour)
            depth_cm = min(25.0, round(4.0 + (area / frame_area) * 85.0 + contrast_diff * 0.15, 1))

            if depth_cm >= 8.0:
                sev = "CRITICAL_P1"
            elif depth_cm >= 5.0:
                sev = "HIGH_P2"
            elif depth_cm >= 3.0:
                sev = "MEDIUM_P3"
            else:
                sev = "LOW_P4"

            conf = min(0.99, max(0.72, round(0.75 + (contrast_diff / 100.0) * 0.20 + (area / frame_area) * 2.0, 3)))

            detections.append({
                "hazard_type": "POTHOLE",
                "rdd_code": "D40 (Pothole / Surface Cavity)",
                "confidence": conf,
                "damage_depth_cm": depth_cm,
                "severity": sev,
                "contour_area": area,
                "bounding_box": {
                    "x": bx,
                    "y": by,
                    "width": bw,
                    "height": bh
                }
            })

        return {
            "frame_width": w,
            "frame_height": h,
            "detections_count": len(detections),
            "detections": detections
        }

    def apply_dpdp_privacy_blur(self, frame: np.ndarray, privacy_boxes: List[Tuple[int, int, int, int]]) -> Tuple[np.ndarray, Dict[str, Any]]:
        redacted = frame.copy()
        for (x, y, bw, bh) in privacy_boxes:
            roi = redacted[y:y+bh, x:x+bw]
            if roi.size > 0:
                ksize = (35, 35)
                blurred_roi = cv2.GaussianBlur(roi, ksize, sigmaX=35, sigmaY=35)
                redacted[y:y+bh, x:x+bw] = blurred_roi

        audit_payload = {
            "dpdp_compliant": True,
            "section": "DPDP Act 2023 §2(t)",
            "faces_masked": sum(1 for box in privacy_boxes if (box[1] + box[3] * 0.5) < frame.shape[0] * 0.40),
            "plates_masked": sum(1 for box in privacy_boxes if (box[1] + box[3] * 0.5) >= frame.shape[0] * 0.40),
            "obfuscation_type": "GAUSSIAN_BLUR_SIGMA_35",
            "zero_storage_persistence": True,
            "volatile_ram_discarded": True,
            "audit_token": f"DPDP-AUDIT-{uuid.uuid4().hex[:8].upper()}"
        }
        return redacted, audit_payload

    @staticmethod
    def measure_laplacian_variance(roi: np.ndarray) -> float:
        if roi.ndim == 3:
            roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        return float(cv2.Laplacian(roi, cv2.CV_64F).var())

# =============================================================================
# 3. Mysuru Transit Corridor Interpolation Engine (Features 7, 8)
# =============================================================================

MYSURU_CORRIDORS: Dict[str, List[Dict[str, Any]]] = {
    "MYSURU_OUTER_RING_ROAD": [
        {"seq": 1, "name": "VVCE Gokulam Junction", "lat": 12.3360, "lng": 76.6210},
        {"seq": 2, "name": "Bogadi Ring Road Junction", "lat": 12.3080, "lng": 76.6120},
        {"seq": 3, "name": "Hunsur Road Flyover Junction", "lat": 12.3210, "lng": 76.6025},
        {"seq": 4, "name": "Hebbal Industrial Area Flyover", "lat": 12.3620, "lng": 76.6180},
        {"seq": 5, "name": "Royal Inn Ring Road Junction", "lat": 12.3735, "lng": 76.6340},
        {"seq": 6, "name": "Columbia Asia Signal Junction", "lat": 12.3480, "lng": 76.6620},
        {"seq": 7, "name": "Bannur Road Ring Road Crossing", "lat": 12.3085, "lng": 76.6850},
        {"seq": 8, "name": "Nanjangud Road Interchange", "lat": 12.2740, "lng": 76.6580},
        {"seq": 9, "name": "Kuvempunagar D-Cross", "lat": 12.2850, "lng": 76.6310},
        {"seq": 10, "name": "Ramakrishnanagar Ring Road", "lat": 12.2960, "lng": 76.6190}
    ],
    "MYSURU_HUNSUR_ROAD": [
        {"seq": 1, "name": "Metropole Circle", "lat": 12.3150, "lng": 76.6480},
        {"seq": 2, "name": "CFTRI Main Gate", "lat": 12.3145, "lng": 76.6410},
        {"seq": 3, "name": "Kalamandira Signal", "lat": 12.3140, "lng": 76.6320},
        {"seq": 4, "name": "Manasagangotri West Gate", "lat": 12.3090, "lng": 76.6275},
        {"seq": 5, "name": "Hunsur Road Ring Road Junction", "lat": 12.3210, "lng": 76.6025}
    ],
    "MYSURU_SAYYAJI_RAO_ROAD": [
        {"seq": 1, "name": "Mysuru Palace North Gate", "lat": 12.3065, "lng": 76.6550},
        {"seq": 2, "name": "K.R. Circle (Chamaraja Wadiyar Statue)", "lat": 12.3095, "lng": 76.6545},
        {"seq": 3, "name": "Ayurvedic Hospital Circle", "lat": 12.3130, "lng": 76.6538},
        {"seq": 4, "name": "Irwin Road Junction", "lat": 12.3168, "lng": 76.6532},
        {"seq": 5, "name": "Government Medical College Crossing", "lat": 12.3215, "lng": 76.6525},
        {"seq": 6, "name": "Highway Circle (BAMMY Park)", "lat": 12.3265, "lng": 76.6518}
    ]
}

def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def calculate_azimuth_bearing(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dlambda = math.radians(lng2 - lng1)
    y = math.sin(dlambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlambda)
    bearing = math.degrees(math.atan2(y, x))
    return (bearing + 360.0) % 360.0

class MysuruCorridorInterpolator:
    def __init__(self, corridor_name: str = "MYSURU_OUTER_RING_ROAD"):
        if corridor_name not in MYSURU_CORRIDORS:
            raise ValueError(f"Unknown corridor: {corridor_name}")
        self.corridor_name = corridor_name
        self.waypoints = MYSURU_CORRIDORS[corridor_name]
        self.segment_distances: List[float] = []
        self.cumulative_distances: List[float] = [0.0]
        
        total = 0.0
        for i in range(len(self.waypoints) - 1):
            w1 = self.waypoints[i]
            w2 = self.waypoints[i+1]
            d = haversine_distance(w1["lat"], w1["lng"], w2["lat"], w2["lng"])
            self.segment_distances.append(d)
            total += d
            self.cumulative_distances.append(total)
        self.total_distance = total

    def interpolate(self, t: float, total_duration: float) -> Dict[str, Any]:
        if total_duration <= 0:
            raise ValueError("total_duration must be strictly positive")
        
        clamped_t = max(0.0, min(float(t), total_duration))
        progress = clamped_t / total_duration
        target_s = progress * self.total_distance

        if target_s >= self.total_distance:
            last = self.waypoints[-1]
            return {
                "lat": last["lat"],
                "lng": last["lng"],
                "bearing": 0.0,
                "segment_index": len(self.waypoints) - 1,
                "location_name": f"{last['name']} ({self.corridor_name})"
            }

        seg_idx = 0
        for i in range(len(self.cumulative_distances) - 1):
            if self.cumulative_distances[i] <= target_s <= self.cumulative_distances[i+1]:
                seg_idx = i
                break

        w1 = self.waypoints[seg_idx]
        w2 = self.waypoints[seg_idx + 1]
        seg_len = self.segment_distances[seg_idx]
        
        alpha = (target_s - self.cumulative_distances[seg_idx]) / seg_len if seg_len > 0 else 0.0

        interp_lat = w1["lat"] + alpha * (w2["lat"] - w1["lat"])
        interp_lng = w1["lng"] + alpha * (w2["lng"] - w1["lng"])
        bearing = calculate_azimuth_bearing(w1["lat"], w1["lng"], w2["lat"], w2["lng"])

        return {
            "lat": round(interp_lat, 6),
            "lng": round(interp_lng, 6),
            "bearing": round(bearing, 1),
            "segment_index": seg_idx,
            "location_name": f"Between {w1['name']} and {w2['name']} ({self.corridor_name})",
            "progress_percent": round(progress * 100.0, 2)
        }

# =============================================================================
# 4. Navigation Guidance, Detour Polylines & Voice Alerts (Features 10, 11, 12)
# =============================================================================

VOICE_ALERT_TEMPLATES = {
    "kn-IN": {
        "POTHOLE": "ಮುಂದೆ {dist} ಮೀಟರ್‌ನಲ್ಲಿ ರಸ್ತೆ ಗುಂಡಿ ಇದೆ. ಎಡ ಪಥಕ್ಕೆ ಬದಲಾಯಿಸಿ ಮತ್ತು ವೇಗ ಕಡಿಮೆ ಮಾಡಿ.",
        "WATERLOGGING": "ಮುಂದೆ {dist} ಮೀಟರ್‌ನಲ್ಲಿ ತೀವ್ರ ನೀರು ನಿಂತಿದೆ. ಎಚ್ಚರಿಕೆ! ನಿಧಾನವಾಗಿ ಚಲಿಸಿ.",
        "ROAD_CRACK": "ಮುಂದೆ {dist} ಮೀಟರ್‌ನಲ್ಲಿ ರಸ್ತೆ ಬಿರುಕು ಇದೆ. ಮಧ್ಯದ ಪಥವನ್ನು ಕಾಯ್ದುಕೊಳ್ಳಿ."
    },
    "hi-IN": {
        "POTHOLE": "आगे {dist} मीटर पर सड़क पर गहरा गड्ढा है। कृपया बाईं लेन में जाएं और गति धीमी करें।",
        "WATERLOGGING": "आगे {dist} मीटर पर भारी जलभराव है। कृपया गति धीमी करें और सावधानी से चलें।",
        "ROAD_CRACK": "आगे {dist} मीटर पर सड़क में दरारें हैं। कृपया लेन के केंद्र में रहें।"
    },
    "en-IN": {
        "POTHOLE": "Warning: Pothole detected {dist} meters ahead. Merge to left lane and reduce speed.",
        "WATERLOGGING": "Warning: Severe waterlogging {dist} meters ahead. Reduce speed to 15 km/h.",
        "ROAD_CRACK": "Caution: Road fissures detected {dist} meters ahead. Maintain center lane alignment."
    }
}

def generate_dynamic_detour_polyline(
    defect_lat: float,
    defect_lng: float,
    bypass_side: str = "LEFT",
    approach_distance_deg: float = 0.0018,
    bypass_offset_deg: float = 0.0006
) -> List[Tuple[float, float]]:
    offset_sign = -1.0 if bypass_side.upper() == "LEFT" else 1.0
    start = (round(defect_lat + approach_distance_deg, 6), round(defect_lng - approach_distance_deg * 0.5, 6))
    decel = (round(defect_lat + approach_distance_deg * 0.4, 6), round(defect_lng - approach_distance_deg * 0.2, 6))
    bypass = (round(defect_lat, 6), round(defect_lng + offset_sign * bypass_offset_deg, 6))
    rejoin = (round(defect_lat - approach_distance_deg * 0.4, 6), round(defect_lng + approach_distance_deg * 0.2, 6))
    clear = (round(defect_lat - approach_distance_deg, 6), round(defect_lng + approach_distance_deg * 0.5, 6))
    return [start, decel, bypass, rejoin, clear]

def render_multilingual_voice_prompt(hazard_type: str, distance_meters: int, lang: str = "kn-IN") -> str:
    h_type = hazard_type.upper()
    if h_type not in ["POTHOLE", "WATERLOGGING", "ROAD_CRACK"]:
        h_type = "POTHOLE"
    template = VOICE_ALERT_TEMPLATES.get(lang, VOICE_ALERT_TEMPLATES["en-IN"]).get(h_type)
    return template.format(dist=distance_meters)

# =============================================================================
# 5. Offline Telemetry & Cloud Synchronization Engine (Features 14, 15)
# =============================================================================

class OfflineTelemetrySyncQueue:
    def __init__(self, bus_id: str = "KSRTC-KA09-E102", max_capacity: int = 1000):
        self.bus_id = bus_id
        self.max_capacity = max_capacity
        self.queue: List[Dict[str, Any]] = []
        self.work_orders_queue: List[Dict[str, Any]] = []
        self.synced_defect_ids: set = set()

    def enqueue_detection(self, detection: Dict[str, Any]) -> bool:
        d_id = detection.get("id")
        if not d_id:
            d_id = f"DEF-{uuid.uuid4().hex[:8].upper()}"
            detection["id"] = d_id
            
        if d_id in self.synced_defect_ids:
            return False

        if len(self.queue) >= self.max_capacity:
            non_p1_idx = next((i for i, item in enumerate(self.queue) if item.get("severity") != "CRITICAL_P1"), None)
            if non_p1_idx is not None:
                self.queue.pop(non_p1_idx)
            else:
                self.queue.pop(0)

        self.queue.append(detection)
        return True

    def enqueue_work_order(self, work_order: Dict[str, Any]) -> bool:
        self.work_orders_queue.append(work_order)
        return True

    def export_batch_payload(self) -> Dict[str, Any]:
        return {
            "bus_id": self.bus_id,
            "batch_timestamp": datetime.now(timezone.utc).isoformat(),
            "detections": list(self.queue),
            "work_orders": list(self.work_orders_queue)
        }

    def acknowledge_sync(self, synced_defect_ids: List[str]) -> int:
        initial_len = len(self.queue)
        self.synced_defect_ids.update(synced_defect_ids)
        self.queue = [item for item in self.queue if item.get("id") not in synced_defect_ids]
        return initial_len - len(self.queue)

    def size(self) -> int:
        return len(self.queue)
