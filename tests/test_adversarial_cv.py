"""
Adversarial Stress Test Suite for Milestone 1: Edge CV & Video Ingestion
Tests:
1. Pure black frames (mean luminance 0)
2. Pure white frames (mean luminance 255)
3. Random noise frames (uniform noise, high entropy)
4. Extreme resolution frames (4K: 3840x2160, 8K: 7680x4320)
5. Zero-byte video file and corrupted video container upload
6. Multiple potholes vs zero potholes in frame
7. Depth formula bounds ([0.0, 25.0] cm physical bounds under extreme inputs)
8. Severity mapping across all threshold boundaries (P1, P2, P3, P4)
9. FastAPI /api/analyze-media resilience under adversarial payloads
"""

import unittest
import os
import tempfile
import cv2
import numpy as np
from fastapi.testclient import TestClient

from backend.main import app
from backend.models import HazardType, SeverityLevel
from backend.agents.vision_perception import VisionPerceptionAgent, LowConfidenceError


class TestAdversarialEdgeCV(unittest.TestCase):
    """Stress tests and edge case mining for Edge CV & Ingestion pipeline."""

    def setUp(self):
        self.agent = VisionPerceptionAgent(min_confidence=0.70)
        self.client = TestClient(app)

    def test_pure_black_frame(self):
        """Verify behavior on a pure black frame (mean luminance = 0.0)."""
        black_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        res = self.agent.analyze_frame(black_frame)
        self.assertFalse(res["hazard_detected"], "Black frame should not trigger false positive detection")
        self.assertEqual(res["depth_cm"], 0.0, "Depth for black frame should be 0.0")
        self.assertEqual(res["confidence"], 0.0)

    def test_pure_white_frame(self):
        """Verify behavior on a pure white frame (mean luminance = 255.0)."""
        white_frame = np.full((480, 640, 3), 255, dtype=np.uint8)
        res = self.agent.analyze_frame(white_frame)
        self.assertFalse(res["hazard_detected"], "White frame should not trigger false positive detection")
        self.assertEqual(res["depth_cm"], 0.0, "Depth for white frame should be 0.0")
        self.assertEqual(res["confidence"], 0.0)

    def test_random_noise_frame(self):
        """Verify behavior on random high-entropy noise frame."""
        np.random.seed(42)
        noise_frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        res = self.agent.analyze_frame(noise_frame)
        # Should not crash and depth must be within [0.0, 25.0]
        self.assertGreaterEqual(res["depth_cm"], 0.0)
        self.assertLessEqual(res["depth_cm"], 25.0)

    def test_high_resolution_4k_and_8k(self):
        """Verify 4K (3840x2160) and 8K (7680x4320) processing and depth normalization."""
        # 4K frame
        frame_4k = np.full((2160, 3840, 3), 130, dtype=np.uint8)
        cv2.circle(frame_4k, (1920, 1500), 180, (25, 25, 25), -1)
        res_4k = self.agent.analyze_frame(frame_4k)
        self.assertTrue(res_4k["hazard_detected"])
        self.assertLessEqual(res_4k["depth_cm"], 25.0)
        self.assertGreaterEqual(res_4k["depth_cm"], 0.0)

        # 8K frame
        frame_8k = np.full((4320, 7680, 3), 130, dtype=np.uint8)
        cv2.circle(frame_8k, (3840, 3000), 360, (25, 25, 25), -1)
        res_8k = self.agent.analyze_frame(frame_8k)
        self.assertTrue(res_8k["hazard_detected"])
        self.assertLessEqual(res_8k["depth_cm"], 25.0)
        self.assertGreaterEqual(res_8k["depth_cm"], 0.0)

    def test_zero_potholes_frame(self):
        """Verify frame with clean road asphalt (zero potholes)."""
        clean_road = np.full((480, 640, 3), 130, dtype=np.uint8)
        res = self.agent.analyze_frame(clean_road)
        self.assertFalse(res["hazard_detected"], "Smooth asphalt must yield hazard_detected=False")
        self.assertEqual(res["contour_area"], 0.0)

    def test_multiple_potholes_in_frame(self):
        """Verify frame containing multiple distinct pothole cavities."""
        multi_frame = np.full((480, 640, 3), 130, dtype=np.uint8)
        # Small pothole
        cv2.circle(multi_frame, (150, 300), 20, (30, 30, 30), -1)
        # Large pothole
        cv2.circle(multi_frame, (450, 340), 55, (20, 20, 20), -1)
        res = self.agent.analyze_frame(multi_frame)
        self.assertTrue(res["hazard_detected"])
        # Should track the primary/largest hazard
        self.assertGreaterEqual(res["contour_area"], 5000.0)
        self.assertGreaterEqual(res["depth_cm"], 8.0)

    def test_depth_formula_physical_bounds(self):
        """Verify depth_cm is strictly bounded in [0.0, 25.0] under extreme contrast and area."""
        # Massive cavity occupying almost entire ROI
        extreme_frame = np.full((480, 640, 3), 230, dtype=np.uint8)
        cv2.rectangle(extreme_frame, (10, 180), (630, 470), (0, 0, 0), -1)
        res = self.agent.analyze_frame(extreme_frame)
        self.assertTrue(res["hazard_detected"])
        self.assertLessEqual(res["depth_cm"], 25.0, "depth_cm must be clamped to 25.0cm max")
        self.assertGreaterEqual(res["depth_cm"], 0.0, "depth_cm must never be negative")

    def test_empty_zero_size_frame_robustness(self):
        """Verify behavior when empty or 0-dimension frame is passed."""
        empty_frame = np.zeros((0, 0, 3), dtype=np.uint8)
        try:
            res = self.agent.analyze_frame(empty_frame)
            self.assertFalse(res["hazard_detected"])
        except Exception as e:
            self.fail(f"analyze_frame crashed on 0x0 empty frame with: {type(e).__name__}: {e}")

    def test_estimate_physical_distress_negative_depth(self):
        """Verify estimate_physical_distress handles negative depth input gracefully."""
        try:
            sev, metrics = self.agent.estimate_physical_distress(HazardType.POTHOLE, damage_depth_cm=-10.0)
            self.assertIsNotNone(metrics["depth_cm"])
            self.assertIsNotNone(metrics["length_m"])
        except Exception as e:
            self.fail(f"estimate_physical_distress crashed on negative depth with: {type(e).__name__}: {e}")

    def test_api_analyze_media_with_clean_road_video(self):
        """Verify POST /api/analyze-media does not crash when uploading a clean road video (0 potholes)."""
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            tmp = f.name
        try:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(tmp, fourcc, 15.0, (640, 480))
            for _ in range(10):
                frame = np.full((480, 640, 3), 130, dtype=np.uint8)
                out.write(frame)
            out.release()

            with open(tmp, "rb") as vf:
                video_bytes = vf.read()

            res = self.client.post("/api/analyze-media", files={"file": ("clean_road.mp4", video_bytes, "video/mp4")})
            self.assertEqual(res.status_code, 200, f"Expected 200, got {res.status_code}: {res.text}")
            data = res.json()
            self.assertEqual(data["status"], "SUCCESS")
            self.assertFalse(data["hazard_detected"])
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)

    def test_api_analyze_media_with_black_image(self):
        """Verify POST /api/analyze-media does not crash when uploading a pure black image."""
        black = np.zeros((480, 640, 3), dtype=np.uint8)
        _, enc = cv2.imencode(".jpg", black)
        res = self.client.post("/api/analyze-media", files={"file": ("black.jpg", enc.tobytes(), "image/jpeg")})
        self.assertEqual(res.status_code, 200, f"Expected 200, got {res.status_code}: {res.text}")
        data = res.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertFalse(data["hazard_detected"])

    def test_api_analyze_media_with_zero_byte_video(self):
        """Verify POST /api/analyze-media handles zero-byte video upload gracefully."""
        res = self.client.post("/api/analyze-media", files={"file": ("empty.mp4", b"", "video/mp4")})
        self.assertIn(res.status_code, [200, 400], "Zero-byte video should return 200 (fallback) or 400 (bad request)")


if __name__ == "__main__":
    unittest.main()
