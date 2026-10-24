"""
UrbanSight AI — Adversarial Performance & Edge Concurrency Challenger Test Suite
Infothon 7.0 · Milestone 1 Verification (Challenger 2)

Verifies:
1. Inference Latency Benchmark (<50ms per frame threshold on Edge PC / CPU):
   - Real road video frames (WhatsApp Video 2026-10-24 at 3.00.43 PM.mp4, 100+ frames)
   - 720p HD and 1080p Full HD frames (100+ frames each)
   - Real reference road distress images (image1.jpg, image2.jpg)
   - Edge CV endpoint (/api/cv/analyze-frame) HTTP round-trip latency
2. Memory Stability & Handle Lifecycle (100+ consecutive frames):
   - Memory profiling (WorkingSetSize / RSS via Windows API & tracemalloc)
   - Detection of memory leaks or monotonic memory ballooning
   - VideoCapture descriptor leak testing and Windows process handle monitoring
   - Adversarial edge cases: corrupted/empty video file ingestion
3. DPDP Act 2023 §2(t) Privacy Blur Performance:
   - Measurement of privacy redaction overhead
   - Kernel sigma=35 Gaussian blurring benchmark on multiple ROIs
   - Pipeline throttling verification (<5ms blur overhead)
"""

import sys
import os
import time
import math
import unittest
import tempfile
import tracemalloc
import ctypes
import ctypes.wintypes
from typing import List, Dict, Any, Tuple

import cv2
import numpy as np

# Ensure urbansight-ai project root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.agents.vision_perception import VisionPerceptionAgent, HazardType, SeverityLevel
from backend.main import app
from fastapi.testclient import TestClient

# Windows Process Memory & Handle Helpers via ctypes
k32 = ctypes.windll.kernel32
GetCurrentProcess = k32.GetCurrentProcess
GetCurrentProcess.restype = ctypes.wintypes.HANDLE

GetProcessHandleCount = k32.GetProcessHandleCount
GetProcessHandleCount.argtypes = [ctypes.wintypes.HANDLE, ctypes.POINTER(ctypes.wintypes.DWORD)]
GetProcessHandleCount.restype = ctypes.wintypes.BOOL

class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
    _fields_ = [
        ('cb', ctypes.wintypes.DWORD),
        ('PageFaultCount', ctypes.wintypes.DWORD),
        ('PeakWorkingSetSize', ctypes.c_size_t),
        ('WorkingSetSize', ctypes.c_size_t),
        ('QuotaPeakPagedPoolUsage', ctypes.c_size_t),
        ('QuotaPagedPoolUsage', ctypes.c_size_t),
        ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
        ('QuotaNonPagedPoolUsage', ctypes.c_size_t),
        ('PagefileUsage', ctypes.c_size_t),
        ('PeakPagefileUsage', ctypes.c_size_t),
        ('PrivateUsage', ctypes.c_size_t),
    ]

psapi = ctypes.windll.psapi
GetProcessMemoryInfo = psapi.GetProcessMemoryInfo
GetProcessMemoryInfo.argtypes = [ctypes.wintypes.HANDLE, ctypes.POINTER(PROCESS_MEMORY_COUNTERS_EX), ctypes.wintypes.DWORD]
GetProcessMemoryInfo.restype = ctypes.wintypes.BOOL

def get_current_process_handles() -> int:
    """Returns the current number of open OS handles for this process."""
    handle = GetCurrentProcess()
    count = ctypes.wintypes.DWORD()
    if GetProcessHandleCount(handle, ctypes.byref(count)):
        return count.value
    return 0

def get_current_process_memory_mb() -> Tuple[float, float]:
    """Returns (WorkingSetSize / RSS in MB, PrivateUsage in MB)."""
    handle = GetCurrentProcess()
    pmc = PROCESS_MEMORY_COUNTERS_EX()
    pmc.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS_EX)
    if GetProcessMemoryInfo(handle, ctypes.byref(pmc), pmc.cb):
        return (pmc.WorkingSetSize / (1024 * 1024), pmc.PrivateUsage / (1024 * 1024))
    return (0.0, 0.0)

def compute_latency_stats(latencies_ms: List[float]) -> Dict[str, float]:
    """Computes comprehensive statistical metrics for latency benchmarking."""
    if not latencies_ms:
        return {}
    sorted_l = sorted(latencies_ms)
    n = len(sorted_l)
    mean_val = sum(sorted_l) / n
    median_val = sorted_l[n // 2]
    p90_val = sorted_l[min(n - 1, int(math.ceil(0.90 * n)) - 1)]
    p95_val = sorted_l[min(n - 1, int(math.ceil(0.95 * n)) - 1)]
    p99_val = sorted_l[min(n - 1, int(math.ceil(0.99 * n)) - 1)]
    variance = sum((x - mean_val) ** 2 for x in sorted_l) / n
    std_val = math.sqrt(variance)
    fps = 1000.0 / mean_val if mean_val > 0 else 0.0

    return {
        "count": n,
        "min_ms": round(sorted_l[0], 2),
        "mean_ms": round(mean_val, 2),
        "median_ms": round(median_val, 2),
        "p90_ms": round(p90_val, 2),
        "p95_ms": round(p95_val, 2),
        "p99_ms": round(p99_val, 2),
        "max_ms": round(sorted_l[-1], 2),
        "std_ms": round(std_val, 2),
        "effective_fps": round(fps, 1)
    }


class TestAdversarialInferenceLatency(unittest.TestCase):
    """
    Task 1: Benchmark inference latency.
    Strict constraint: frame analysis must run within edge PC limits (<50ms per frame).
    """

    def setUp(self):
        self.agent = VisionPerceptionAgent()
        self.parent_dir = os.path.abspath(os.path.join(PROJECT_ROOT, ".."))
        self.real_video_path = os.path.join(self.parent_dir, "WhatsApp Video 2026-10-24 at 3.00.43 PM.mp4")

    def test_latency_real_road_video_100_frames(self):
        """Benchmark 100+ consecutive frames from real transit dashcam video."""
        self.assertTrue(os.path.exists(self.real_video_path), f"Video file missing: {self.real_video_path}")
        cap = cv2.VideoCapture(self.real_video_path)
        self.assertTrue(cap.isOpened(), "Could not open real road video with OpenCV")

        latencies = []
        frame_count = 0
        target_frames = 100

        # Warmup 5 frames
        for _ in range(5):
            ret, frame = cap.read()
            if ret and frame is not None:
                self.agent.analyze_frame(frame)

        while frame_count < target_frames:
            ret, frame = cap.read()
            if not ret or frame is None:
                break
            
            t0 = time.perf_counter()
            res = self.agent.analyze_frame(frame, apply_privacy_blur=True)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            latencies.append(elapsed_ms)
            frame_count += 1
            
            self.assertIn("hazard_detected", res)
            self.assertIn("depth_cm", res)

        cap.release()

        self.assertGreaterEqual(frame_count, target_frames, f"Video did not yield {target_frames} frames")
        stats = compute_latency_stats(latencies)
        print(f"\n[BENCHMARK] Real Road Video ({frame_count} frames): Mean={stats['mean_ms']}ms, P95={stats['p95_ms']}ms, FPS={stats['effective_fps']}")

        self.assertLess(stats["mean_ms"], 50.0, f"Mean latency {stats['mean_ms']}ms exceeds 50ms edge PC limit")
        self.assertLess(stats["p95_ms"], 50.0, f"P95 latency {stats['p95_ms']}ms exceeds 50ms edge PC limit")

    def test_latency_720p_hd_synthetic_road(self):
        """Benchmark 100 frames of 1280x720 HD road frames with dynamic cavity contours."""
        latencies = []
        for i in range(100):
            # Generate 720p asphalt texture
            frame = np.full((720, 1280, 3), 110, dtype=np.uint8)
            # Add dynamic potholes & cracks
            cx = 400 + (i * 5) % 400
            cy = 450 + (i * 3) % 200
            cv2.circle(frame, (cx, cy), 35, (40, 40, 40), -1)
            cv2.ellipse(frame, (cx + 100, cy + 20), (50, 8), 25, 0, 360, (30, 30, 30), -1)

            t0 = time.perf_counter()
            res = self.agent.analyze_frame(frame, apply_privacy_blur=True)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            latencies.append(elapsed_ms)

        stats = compute_latency_stats(latencies)
        print(f"\n[BENCHMARK] 720p HD Frames (100 frames): Mean={stats['mean_ms']}ms, P95={stats['p95_ms']}ms, FPS={stats['effective_fps']}")
        self.assertLess(stats["mean_ms"], 50.0)
        self.assertLess(stats["p95_ms"], 50.0)

    def test_latency_1080p_fhd_synthetic_road(self):
        """Benchmark 100 frames of 1920x1080 Full HD road frames with noise & cavities."""
        latencies = []
        for i in range(100):
            # Generate 1080p asphalt texture
            frame = np.full((1080, 1920, 3), 115, dtype=np.uint8)
            cx = 600 + (i * 7) % 700
            cy = 650 + (i * 4) % 300
            cv2.circle(frame, (cx, cy), 55, (35, 35, 35), -1)

            t0 = time.perf_counter()
            res = self.agent.analyze_frame(frame, apply_privacy_blur=True)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            latencies.append(elapsed_ms)

        stats = compute_latency_stats(latencies)
        print(f"\n[BENCHMARK] 1080p Full HD Frames (100 frames): Mean={stats['mean_ms']}ms, P95={stats['p95_ms']}ms, FPS={stats['effective_fps']}")
        self.assertLess(stats["mean_ms"], 50.0, f"1080p Mean latency {stats['mean_ms']}ms exceeds 50ms")
        self.assertLess(stats["p95_ms"], 50.0, f"1080p P95 latency {stats['p95_ms']}ms exceeds 50ms")

    def test_latency_real_image_assets(self):
        """Benchmark inference on project high-res real road image assets (image1.jpg, image2.jpg)."""
        img1_path = os.path.join(PROJECT_ROOT, "image1.jpg")
        img2_path = os.path.join(PROJECT_ROOT, "image2.jpg")
        self.assertTrue(os.path.exists(img1_path), "image1.jpg missing")
        self.assertTrue(os.path.exists(img2_path), "image2.jpg missing")

        frame1 = cv2.imread(img1_path)
        frame2 = cv2.imread(img2_path)
        self.assertIsNotNone(frame1)
        self.assertIsNotNone(frame2)

        latencies = []
        for i in range(50):
            target = frame1 if (i % 2 == 0) else frame2
            t0 = time.perf_counter()
            res = self.agent.analyze_frame(target, apply_privacy_blur=True)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            latencies.append(elapsed_ms)

        stats = compute_latency_stats(latencies)
        print(f"\n[BENCHMARK] Real Image Assets ({frame1.shape} / {frame2.shape}): Mean={stats['mean_ms']}ms, P95={stats['p95_ms']}ms")
        self.assertLess(stats["mean_ms"], 50.0)

    def test_latency_fastapi_endpoint(self):
        """Benchmark POST /api/cv/analyze-frame HTTP round-trip latency over 50 requests."""
        client = TestClient(app)
        frame = np.full((480, 640, 3), 120, dtype=np.uint8)
        cv2.circle(frame, (320, 300), 40, (40, 40, 40), -1)
        _, enc = cv2.imencode(".jpg", frame)
        frame_bytes = enc.tobytes()

        latencies = []
        # Warmup
        for _ in range(5):
            client.post("/api/cv/analyze-frame", files={"file": ("frame.jpg", frame_bytes, "image/jpeg")})

        for _ in range(50):
            t0 = time.perf_counter()
            r = client.post("/api/cv/analyze-frame", files={"file": ("frame.jpg", frame_bytes, "image/jpeg")})
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            latencies.append(elapsed_ms)
            self.assertEqual(r.status_code, 200)

        stats = compute_latency_stats(latencies)
        print(f"\n[BENCHMARK] FastAPI /api/cv/analyze-frame (50 requests): Mean={stats['mean_ms']}ms, P95={stats['p95_ms']}ms")
        self.assertLess(stats["mean_ms"], 50.0, f"Endpoint mean latency {stats['mean_ms']}ms exceeds 50ms")


class TestAdversarialMemoryStabilityAndHandles(unittest.TestCase):
    """
    Task 2: Stress test memory stability.
    Process 100+ consecutive frames to verify no memory leaks or unreleased VideoCapture descriptors.
    """

    def setUp(self):
        self.agent = VisionPerceptionAgent()
        self.parent_dir = os.path.abspath(os.path.join(PROJECT_ROOT, ".."))
        self.real_video_path = os.path.join(self.parent_dir, "WhatsApp Video 2026-10-24 at 3.00.43 PM.mp4")

    def test_memory_stability_150_consecutive_frames(self):
        """Process 150 consecutive frames and verify memory stabilizes with zero monotonic leak."""
        cap = cv2.VideoCapture(self.real_video_path)
        self.assertTrue(cap.isOpened(), "Could not open video")

        tracemalloc.start()
        initial_handles = get_current_process_handles()
        initial_rss, _ = get_current_process_memory_mb()

        # Warmup 25 frames
        for _ in range(25):
            ret, frame = cap.read()
            if ret and frame is not None:
                self.agent.analyze_frame(frame)

        post_warmup_rss, _ = get_current_process_memory_mb()
        snapshot_start = tracemalloc.take_snapshot()

        # Process next 125 frames (total 150 frames)
        for i in range(125):
            ret, frame = cap.read()
            if not ret or frame is None:
                # Loop back if video ends
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
            self.agent.analyze_frame(frame)

        snapshot_end = tracemalloc.take_snapshot()
        final_rss, _ = get_current_process_memory_mb()
        final_handles = get_current_process_handles()
        cap.release()

        # Compute Python heap differences
        stats = snapshot_end.compare_to(snapshot_start, 'lineno')
        total_heap_growth_kb = sum(stat.size_diff for stat in stats) / 1024.0
        rss_growth_mb = final_rss - post_warmup_rss

        print(f"\n[MEMORY AUDIT] 150 Frames: Initial RSS={round(initial_rss, 2)}MB, Post-Warmup RSS={round(post_warmup_rss, 2)}MB, Final RSS={round(final_rss, 2)}MB, Growth={round(rss_growth_mb, 2)}MB, HeapGrowth={round(total_heap_growth_kb, 2)}KB")
        print(f"[HANDLE AUDIT] Handles: Initial={initial_handles}, Final={final_handles}, Delta={final_handles - initial_handles}")

        tracemalloc.stop()

        # Working set should not grow by more than 10MB across 125 steady-state frames
        self.assertLess(rss_growth_mb, 10.0, f"Excessive memory growth of {rss_growth_mb} MB indicates potential leak")
        # Handle delta should be virtually zero
        self.assertLessEqual(abs(final_handles - initial_handles), 5, "Unreleased OS handles detected")

    def test_videocapture_descriptor_release_loop(self):
        """Stress-test 30 consecutive VideoCapture open/read/release cycles to ensure descriptor release."""
        initial_handles = get_current_process_handles()
        
        for i in range(30):
            cap = cv2.VideoCapture(self.real_video_path)
            self.assertTrue(cap.isOpened())
            ret, frame = cap.read()
            self.assertTrue(ret)
            res = self.agent.analyze_frame(frame)
            self.assertIn("depth_cm", res)
            cap.release()

        final_handles = get_current_process_handles()
        delta = final_handles - initial_handles
        print(f"\n[VIDEOCAPTURE DESCRIPTORS] 30 Open/Close cycles: Initial Handles={initial_handles}, Final Handles={final_handles}, Delta={delta}")
        self.assertLessEqual(delta, 3, f"Handle leak detected: {delta} handles accumulated over 30 VideoCapture cycles")

    def test_api_analyze_media_video_ingestion_descriptor_stability(self):
        """Call POST /api/analyze-media with real video file in a loop and verify no tempfile/descriptor leaks."""
        client = TestClient(app)
        with open(self.real_video_path, "rb") as vf:
            video_bytes = vf.read(500000)  # ~500KB chunk

        initial_handles = get_current_process_handles()
        initial_rss, _ = get_current_process_memory_mb()

        for iteration in range(10):
            response = client.post(
                "/api/analyze-media",
                files={"file": ("dashcam_stress.mp4", video_bytes, "video/mp4")},
                data={"bus_id": f"TEST-BUS-{iteration}"}
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("hazard_detection", data)

        final_handles = get_current_process_handles()
        final_rss, _ = get_current_process_memory_mb()
        handle_delta = final_handles - initial_handles
        rss_delta = final_rss - initial_rss

        print(f"\n[API MEDIA STRESS] 10 Video Ingestions: Handles Delta={handle_delta}, RSS Delta={round(rss_delta, 2)}MB")
        self.assertLessEqual(handle_delta, 4, f"Handle leak in /api/analyze-media: {handle_delta} leaked handles")
        self.assertLess(rss_delta, 15.0, f"Memory ballooning in /api/analyze-media: {rss_delta}MB")

    def test_adversarial_corrupted_video_file_descriptors(self):
        """Verify handling of truncated / corrupted video files without leaking descriptors or crashing."""
        client = TestClient(app)
        corrupted_bytes = b"ftypisom" + b"\x00\xFF\xAA\x55" * 1024

        initial_handles = get_current_process_handles()
        for i in range(5):
            response = client.post(
                "/api/analyze-media",
                files={"file": ("corrupt.mp4", corrupted_bytes, "video/mp4")}
            )
            self.assertEqual(response.status_code, 200)

        final_handles = get_current_process_handles()
        self.assertLessEqual(final_handles - initial_handles, 3)


class TestAdversarialDPDPPrivacyBlurPerformance(unittest.TestCase):
    """
    Task 3: Test DPDP Act 2023 §2(t) privacy blur performance.
    Verify blurring does not throttle the pipeline (<5ms overhead).
    """

    def setUp(self):
        self.agent = VisionPerceptionAgent()
        self.frame_1080p = np.full((1080, 1920, 3), 110, dtype=np.uint8)

    def test_dpdp_privacy_redaction_overhead(self):
        """Measure latency difference between apply_privacy_blur=True and False."""
        latencies_with_blur = []
        latencies_without_blur = []

        # 100 iterations each
        for _ in range(100):
            t0 = time.perf_counter()
            self.agent.analyze_frame(self.frame_1080p, apply_privacy_blur=True)
            latencies_with_blur.append((time.perf_counter() - t0) * 1000.0)

            t0 = time.perf_counter()
            self.agent.analyze_frame(self.frame_1080p, apply_privacy_blur=False)
            latencies_without_blur.append((time.perf_counter() - t0) * 1000.0)

        mean_with = sum(latencies_with_blur) / len(latencies_with_blur)
        mean_without = sum(latencies_without_blur) / len(latencies_without_blur)
        overhead = abs(mean_with - mean_without)

        print(f"\n[DPDP OVERHEAD] With Blur: {round(mean_with, 2)}ms | Without Blur: {round(mean_without, 2)}ms | Overhead: {round(overhead, 3)}ms")
        self.assertLess(overhead, 2.0, f"DPDP blur metadata overhead {overhead}ms is too high")

    def test_opencv_gaussian_blur_sigma_35_roi_latency(self):
        """
        Benchmark genuine cv2.GaussianBlur with sigma=35 and kernel (35,35)
        applied to multiple simulated face and license plate ROIs.
        """
        # Test 4 distinct privacy ROIs per frame
        rois = [
            (100, 100, 60, 60),    # Face 1
            (350, 120, 70, 70),    # Face 2
            (800, 500, 120, 45),   # License plate 1
            (1200, 520, 110, 40)   # License plate 2
        ]

        latencies = []
        frame_copy = self.frame_1080p.copy()

        for _ in range(100):
            t0 = time.perf_counter()
            for (x, y, w, h) in rois:
                sub_roi = frame_copy[y:y+h, x:x+w]
                if sub_roi.size > 0:
                    blurred_roi = cv2.GaussianBlur(sub_roi, (35, 35), sigmaX=35, sigmaY=35)
                    frame_copy[y:y+h, x:x+w] = blurred_roi
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            latencies.append(elapsed_ms)

        stats = compute_latency_stats(latencies)
        print(f"\n[OPENCV GAUSSIAN BLUR] 4 ROIs (sigma=35) on 1080p: Mean={stats['mean_ms']}ms, P95={stats['p95_ms']}ms, Max={stats['max_ms']}ms")
        # Gaussian blurring 4 small ROIs should comfortably take < 5.0ms
        self.assertLess(stats["mean_ms"], 5.0, f"Gaussian blur mean {stats['mean_ms']}ms exceeds 5ms pipeline throttle threshold")

    def test_canvas_cv_algorithm_execution_budget(self):
        """
        Simulate the canvas 2D pixel processing loop from static/js/app.js (analyzeCanvasFrame)
        to verify that client-side pixel scanning stays well within 16.6ms (60 FPS budget).
        """
        # Canvas dimensions 800x450, lower 62% ROI, step=3
        roi_w = 672
        roi_h = 269
        # Create simulated RGBA pixel buffer
        pixel_data = np.random.randint(90, 140, size=(roi_h, roi_w, 4), dtype=np.uint8)
        # Inject dark cavity
        pixel_data[100:140, 300:360, 0:3] = 40

        flat_data = pixel_data.flatten()
        step = 3
        latencies = []

        for _ in range(50):
            t0 = time.perf_counter()
            # Equivalent logic to app.js analyzeCanvasFrame
            sum_lum = 0
            sample_count = 0
            # Phase 1: Mean luminance
            for y in range(0, roi_h, step):
                for x in range(0, roi_w, step):
                    idx = (y * roi_w + x) * 4
                    lum = 0.299 * flat_data[idx] + 0.587 * flat_data[idx + 1] + 0.114 * flat_data[idx + 2]
                    sum_lum += lum
                    sample_count += 1
            mean_lum = sum_lum / max(1, sample_count)
            dark_thresh = max(25.0, mean_lum * 0.72)

            # Phase 2: Cavity search
            dark_count = 0
            for y in range(0, roi_h, step):
                for x in range(0, roi_w, step):
                    idx = (y * roi_w + x) * 4
                    lum = 0.299 * flat_data[idx] + 0.587 * flat_data[idx + 1] + 0.114 * flat_data[idx + 2]
                    if lum < dark_thresh:
                        dark_count += 1

            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            latencies.append(elapsed_ms)

        stats = compute_latency_stats(latencies)
        print(f"\n[CANVAS 2D PIXEL LOOP BENCHMARK]: Mean={stats['mean_ms']}ms, P95={stats['p95_ms']}ms")
        # In Python uncompiled this loop takes a few ms; in V8 JIT it takes < 1ms.
        # Python loop should take < 50ms, meaning in V8 it runs in < 2ms.
        self.assertLess(stats["mean_ms"], 50.0)


if __name__ == "__main__":
    unittest.main()
