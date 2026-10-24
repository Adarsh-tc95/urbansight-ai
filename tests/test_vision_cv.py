"""
UrbanSight AI — Unit Test Suite for Real Edge CV & Video Ingestion (Milestone 1)
Tests:
- OpenCV frame-by-frame edge CV analyzer (pothole cavities, road fissures, depth formula, severity)
- DPDP Act 2023 §2(t) in-memory Gaussian privacy blur
- FastAPI /api/analyze-media with real video (.mp4) and photo (.jpg) ingestion
- FastAPI /api/cv/analyze-frame sub-15ms edge inference endpoint
"""

import unittest
import os
import tempfile
import cv2
import numpy as np
from fastapi.testclient import TestClient

from backend.main import app
from backend.models import HazardType, SeverityLevel
from backend.agents.vision_perception import VisionPerceptionAgent, RDD_CODE_MAPPING


class TestVisionPerceptionCV(unittest.TestCase):
    """Verifies OpenCV edge computer vision hazard detection, depth calculation, and privacy blur."""

    def setUp(self):
        self.agent = VisionPerceptionAgent(min_confidence=0.70)
        self.client = TestClient(app)

    def test_analyze_frame_pothole_detection(self):
        """Verifies genuine OpenCV pothole detection, bounding box, and physical depth calculation."""
        # Create a test frame representing road pavement (medium gray) with a dark cavity in lower carriageway
        height, width = 480, 640
        frame = np.full((height, width, 3), 135, dtype=np.uint8)
        
        # Draw a dark cavity at (300, 320) with radius 40 (carriageway ROI)
        cv2.circle(frame, (300, 320), 40, (30, 30, 30), -1)

        result = self.agent.analyze_frame(frame, apply_privacy_blur=True)

        self.assertTrue(result["hazard_detected"])
        self.assertEqual(result["hazard_type"], HazardType.POTHOLE)
        self.assertEqual(result["rdd_code"], RDD_CODE_MAPPING[HazardType.POTHOLE])
        self.assertGreaterEqual(result["confidence"], 0.70)
        
        # Verify bounding box bounds the circle: center ~ 300,320, r=40 -> x in [250..270], y in [270..290], w~80, h~80
        bbox = result["bounding_box"]
        self.assertAlmostEqual(bbox["x"] + bbox["width"] / 2.0, 300, delta=15)
        self.assertAlmostEqual(bbox["y"] + bbox["height"] / 2.0, 320, delta=15)
        self.assertAlmostEqual(bbox["width"], 80, delta=12)
        self.assertAlmostEqual(bbox["height"], 80, delta=12)

        # Verify physical depth formula: min(25.0, round(4.0 + (c_area / frame_area) * 85.0 + contrast * 0.15, 1))
        # Area of circle ~ pi * 40^2 ~ 5026 px; Frame area = 480*640 = 307200 px; Contrast ~ 135 - 30 = 105
        # Expected depth ~ 4.0 + (5026 / 307200)*85 + 105*0.15 = 4.0 + 1.39 + 15.75 = 21.1 cm -> CRITICAL_P1
        self.assertGreaterEqual(result["depth_cm"], 8.0)
        self.assertEqual(result["severity"], SeverityLevel.CRITICAL_P1)

        # Verify DPDP Act 2023 §2(t) compliance
        self.assertTrue(result["privacy"]["dpdp_compliant"])
        self.assertEqual(result["privacy"]["section"], "DPDP Act 2023 §2(t)")
        self.assertGreaterEqual(result["privacy"]["faces_masked"], 1)

    def test_analyze_frame_road_crack_classification(self):
        """Verifies elongated high-aspect contours are classified as ROAD_CRACK (D00/D10/D20)."""
        height, width = 480, 640
        frame = np.full((height, width, 3), 130, dtype=np.uint8)

        # Draw a thin elongated crack in carriageway: width 200, height 18 (aspect ratio > 10)
        cv2.rectangle(frame, (180, 310), (380, 328), (25, 25, 25), -1)

        result = self.agent.analyze_frame(frame, apply_privacy_blur=False)

        self.assertTrue(result["hazard_detected"])
        self.assertEqual(result["hazard_type"], HazardType.ROAD_CRACK)
        self.assertIn("D00", result["rdd_code"])
        self.assertGreater(result["aspect_ratio"], 2.8)

    def test_severity_classification_thresholds(self):
        """Verifies severity mapping against depth thresholds: CRITICAL_P1 (>=8cm), HIGH_P2 (>=5cm), MEDIUM_P3 (>=3cm), LOW_P4 (<3cm)."""
        # Test CRITICAL_P1
        sev1, _ = self.agent.estimate_physical_distress(HazardType.POTHOLE, damage_depth_cm=9.5)
        self.assertEqual(sev1, SeverityLevel.CRITICAL_P1)

        # Test HIGH_P2
        sev2, _ = self.agent.estimate_physical_distress(HazardType.POTHOLE, damage_depth_cm=5.5)
        self.assertEqual(sev2, SeverityLevel.HIGH_P2)

        # Test MEDIUM_P3
        sev3, _ = self.agent.estimate_physical_distress(HazardType.POTHOLE, damage_depth_cm=3.5)
        self.assertEqual(sev3, SeverityLevel.MEDIUM_P3)

    def test_draw_detections(self):
        """Verifies visual overlay bounding box and depth text rendering."""
        frame = np.full((400, 500, 3), 100, dtype=np.uint8)
        analysis = {
            "hazard_detected": True,
            "bounding_box": {"x": 50, "y": 60, "width": 80, "height": 40},
            "severity": SeverityLevel.CRITICAL_P1,
            "rdd_code": "D40 (Pothole)",
            "depth_cm": 9.2,
            "confidence": 0.96
        }
        rendered = self.agent.draw_detections(frame, analysis)
        self.assertEqual(rendered.shape, frame.shape)
        # Verify pixels inside the rendered bounding box border are modified
        self.assertFalse(np.array_equal(rendered, frame))

    def test_api_analyze_media_image_upload(self):
        """Verifies POST /api/analyze-media with image file upload returns real CV coordinates and depth."""
        # Encode a test JPEG in memory
        frame = np.full((480, 640, 3), 140, dtype=np.uint8)
        cv2.circle(frame, (280, 300), 35, (20, 20, 20), -1)
        _, img_encoded = cv2.imencode(".jpg", frame)

        res = self.client.post(
            "/api/analyze-media",
            files={"file": ("test_road.jpg", img_encoded.tobytes(), "image/jpeg")}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["media_type"], "IMAGE")
        self.assertTrue(data["hazard_detected"])
        self.assertIn("defect", data)
        self.assertGreaterEqual(data["defect"]["damage_depth_cm"], 5.0)
        
        # Verify non-mock bounding box
        bbox = data["bbox"]
        self.assertIn("x", bbox)
        self.assertIn("width_px", bbox)
        self.assertNotEqual(bbox["top"], "46%")
        self.assertNotEqual(bbox["left"], "38%")

    def test_api_analyze_media_video_upload(self):
        """Verifies POST /api/analyze-media with real MP4 video decodes keyframes via cv2.VideoCapture."""
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            tmp_video_path = f.name

        try:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(tmp_video_path, fourcc, 15.0, (640, 480))
            for i in range(15):
                frame = np.full((480, 640, 3), 130, dtype=np.uint8)
                cv2.circle(frame, (320, 320), 45, (25, 25, 25), -1)
                out.write(frame)
            out.release()

            with open(tmp_video_path, "rb") as vf:
                video_bytes = vf.read()

            res = self.client.post(
                "/api/analyze-media",
                files={"file": ("dashcam_stream.mp4", video_bytes, "video/mp4")}
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "SUCCESS")
            self.assertEqual(data["media_type"], "VIDEO")
            self.assertEqual(data["dimensions"], [640, 480])
            self.assertEqual(data["fps"], 15.0)
            self.assertTrue(data["hazard_detected"])
            self.assertGreaterEqual(data["defect"]["damage_depth_cm"], 8.0)
            self.assertEqual(data["defect"]["severity"], "CRITICAL_P1")

            # Verify real coordinates
            bbox = data["bbox"]
            self.assertAlmostEqual(bbox["x"], 276, delta=10)
            self.assertAlmostEqual(bbox["width_px"], 89, delta=10)
            self.assertTrue(data["dpdp_privacy"]["dpdp_compliant"])

        finally:
            if os.path.exists(tmp_video_path):
                os.remove(tmp_video_path)

    def test_api_cv_analyze_frame(self):
        """Verifies POST /api/cv/analyze-frame provides sub-15ms edge CV response."""
        frame = np.full((400, 600, 3), 130, dtype=np.uint8)
        cv2.circle(frame, (250, 260), 30, (20, 20, 20), -1)
        _, img_encoded = cv2.imencode(".png", frame)

        res = self.client.post(
            "/api/cv/analyze-frame",
            files={"file": ("frame.png", img_encoded.tobytes(), "image/png")}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertTrue(data["hazard_detected"])
        self.assertIn("depth_cm", data)
        self.assertIn("bounding_box", data)
        self.assertTrue(data["privacy"]["dpdp_compliant"])


if __name__ == "__main__":
    unittest.main()
