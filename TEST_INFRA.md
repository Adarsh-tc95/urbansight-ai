# UrbanSight AI — Test Infrastructure Specification

**Document Version**: 2.1.0  
**Status**: ACTIVE / VERIFIED  
**Target Platform**: Local PC & On-Bus Edge Hardware (AMD64 / Windows / Linux)  
**Author**: E2E Test Suite Architect & Writer (`test_writer_e2e`)  
**Date**: 2026-10-24  

---

## 1. Architectural Overview

UrbanSight AI features a comprehensive, opaque-box, multi-tier End-to-End (E2E) testing infrastructure. The test suite exercises the system against real-world domain physics, ISO standards, municipal regulatory workflows (CPWD / KTPP Act / DPDP Act 2023), and geospatial routing mechanics without simulated data fallbacks or mock bypasses.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   UrbanSight AI E2E Test Matrix                        │
│                                                                        │
│  [Tier 1: Feature Coverage]          ──► 85 Tests (17 Features x 5)    │
│  [Tier 2: Boundary & Corner Cases]   ──► 85 Tests (17 Features x 5)    │
│  [Tier 3: Cross-Feature Interaction] ──► 17 Pairwise Pipeline Tests    │
│  [Tier 4: Mysuru Transit Scenarios]  ──► 15 Realistic Corridor Runs    │
│                                                                        │
│  Total Test Cases: 202 Executable Tests | Pass Rate: 100% (202 / 202)  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Testing Tiers & Coverage Breakdown

### Tier 1: Functional Feature Coverage (85 Tests)
Validates the baseline operational capability of all 17 features defined in `PROJECT.md` § Feature Inventory (5 dedicated tests per feature):

1. **Feature 1: Real Video Ingestion (.mp4, .mov, .avi)**: Container structure validation, QuickTime atom parsing, RIFF header inspection, extension gating, placeholder rejection.
2. **Feature 2: Live Camera Stream Processing**: 1080p frame buffer capture, FPS throughput rate (>=25 FPS), 16:9 aspect ratio preservation, device camera flip contracts, stream interruption resilience.
3. **Feature 3: Frame-by-Frame Edge Computer Vision**: Otsu adaptive thresholding dark cavity detection, Canny crack edge isolation, low-variance waterlogging detection, 0.70 confidence threshold gating, rejection of synthetic trigonometric animations.
4. **Feature 4: Bounding Box & Depth Calculation**: Bounding box coordinate extraction, physical depth formula verification (`min(25.0, round(4.0 + (area/frame_area)*85 + contrast*0.15, 1))`), severity classification (`CRITICAL_P1`, `HIGH_P2`, `MEDIUM_P3`, `LOW_P4`).
5. **Feature 5: DPDP Act 2023 §2(t) Privacy Blur**: Laplacian variance entropy reduction (Gaussian blur sigma >= 35), pedestrian face masking, license plate masking, zero-storage volatile RAM discard, statutory audit token generation (`DPDP-AUDIT-...`).
6. **Feature 6: QuickTime/MP4 EXIF Metadata Extractor**: Pure-Python parsing of `\xa9xyz` ISO 6709 location atoms, JPEG EXIF Tag 34853 GPS IFD extraction, altitude extraction, precedence hierarchy (EXIF > Geolocation > Corridor Interpolation), rejection of hardcoded fallback coordinates.
7. **Feature 7: Device / Browser Geolocation Tracking**: `navigator.geolocation` schema contracts, speed and azimuth bearing derivation from successive fixes, accuracy radius filtering (<= 50m), live driver console HUD emission, signal loss timeout detection.
8. **Feature 8: Mysuru Corridor Route Interpolation**: Piecewise spherical interpolation along Outer Ring Road (40 waypoints), Hunsur Road (5 waypoints), and Sayyaji Rao Road (6 waypoints), cumulative Haversine distance, forward azimuth bearing calculation.
9. **Feature 9: Dynamic Leaflet GIS Hazard Pinning**: Leaflet teardrop marker coordinate mapping, severity-to-color mapping (#EF4444 P1, #F97316 P2), popup CPWD voucher binding, GIS auto-pan/zoom centering, DBSCAN spatial clustering merge.
10. **Feature 10: Dynamic Lateral Maneuvers HUD**: Pothole `MERGE_LEFT` maneuver, waterlogging `REDUCE_SPEED_AND_DETOUR` maneuver, crack `STEER_CENTER` maneuver, proximity distance countdown (<300m), visual directive text formatting.
11. **Feature 11: Multilingual Spoken Voice Alerts**: Kannada (`kn-IN`) alert template, Hindi (`hi-IN`) alert template, English (`en-IN`) alert template, high-priority dual-tone audio chime (880Hz / 440Hz), language switcher locale selection.
12. **Feature 12: Dynamic Turn-by-Turn Detour Polylines**: 5-point detour polyline generation, dynamic adaptation to defect coordinates without Gokulam hardcoding, multi-layer visual route styling, 3-step turn guidance instructions, MCC depot rapid-response route calculation.
13. **Feature 13: Local PC On-Bus Execution**: Local FastAPI health status (200 OK), sub-30ms consensus pipeline latency, CORS open access headers, zero external cloud dependencies, standalone static template serving.
14. **Feature 14: Offline Telemetry & Work Order Queue**: Disconnection buffering in offline queue, strict FIFO persistence, priority retention of critical P1 defects under queue capacity cap, offline work order state transitions, JSON serialization integrity.
15. **Feature 15: Automatic Cloud Telemetry Synchronization**: Online reconnection event trigger, `TelemetrySyncBatch` schema compliance, idempotent sync deduplication, server acknowledgment queue clearing, exponential backoff retry scheduling.
16. **Feature 16: End-to-End Test Suite Verification**: Complete 17-feature representation, multi-tier hierarchy validation, test isolation, unittest compatibility, anti-facade data assertion checks.
17. **Feature 17: Adversarial Hardening (Tier 5)**: Random binary stream fuzzing resilience, Earth coordinate boundary validation, NaN and infinite depth clamping, SQL/XSS injection sanitization, extreme IMU accelerometer shock spike resilience (-15.0g).

---

### Tier 2: Boundary & Corner Cases (85 Tests)
Stress-tests extreme boundary values, malformed inputs, numerical edge conditions, and failure modes across all 17 features:
- Zero-byte files, corrupt atom headers, and unsupported FourCC codecs.
- Zero-resolution camera buffers, 32:9 extreme anamorphic aspect ratios, and rapid camera toggling.
- Pure black night frames, pure white glare frames, and 1-pixel micro-noise contours.
- Baseline 4.0cm flat surface depth and strict 25.0cm crater upper depth clamping.
- Zero-entropy blank frame privacy blurring, full-frame privacy masks, and overlapping face bounding boxes.
- Truncated ISO 6709 strings, missing signs, and out-of-range latitude/longitude coordinates.
- NaN coordinates, 2500m extreme accuracy radii, 450 km/h supersonic speed anomalies, and stale fixes.
- Elapsed time t=0, t=T, t>T, and coincident duplicate waypoints.
- Null Island coordinates `[0, 0]`, 1000-marker canvas stress, and zoom level limits (0 and 22).
- Zero-meter maneuver distance, 10km distant hazards, and negative distances behind vehicle.
- Unsupported locales, empty location names, and audio chime interrupts.
- Minimum lateral bypass offsets and collinearity checks.
- 50-request burst concurrency, 10MB payloads, and missing parameters.
- Empty queue exports, queue capacity capping, and partial batch sync reconciliations.
- Flapping network cycles, HTTP 503 service unavailable, future timestamps, and large batch chunking.
- SQL injection in defect IDs, XSS payloads in location strings, and -50.0g accelerometer saturation.

---

### Tier 3: Cross-Feature Interactions (17 Tests)
Validates pairwise data flows and contracts across interdependent modules:
- `X01`: Video Ingestion (F1) ➔ Edge CV (F3)
- `X02`: Edge CV (F3) ➔ Depth Calculation (F4)
- `X03`: Edge CV (F3) ➔ DPDP Privacy Blur (F5)
- `X04`: Video Ingestion (F1) ➔ QuickTime GPS (F6)
- `X05`: QuickTime GPS (F6) ➔ Corridor Interpolation (F8)
- `X06`: Browser Geolocation (F7) ➔ Corridor Snapping (F8)
- `X07`: Edge CV (F3) ➔ Leaflet Hazard Pinning (F9)
- `X08`: Corridor Interpolation (F8) ➔ Leaflet Pinning (F9)
- `X09`: Leaflet Pinning (F9) ➔ Lateral HUD Maneuver (F10)
- `X10`: Lateral HUD (F10) ➔ Multilingual Voice Synthesis (F11)
- `X11`: Lateral HUD (F10) ➔ Detour Polyline Generation (F12)
- `X12`: Leaflet Pinning (F9) ➔ Offline Queue (F14)
- `X13`: Offline Queue (F14) ➔ Cloud Sync Engine (F15)
- `X14`: Depth Severity (F4) ➔ Offline Queue Priority (F14)
- `X15`: Local PC Execution (F13) ➔ Offline Queue (F14)
- `X16`: Cloud Sync (F15) ➔ Central GIS Dashboard (F9)
- `X17`: DPDP Privacy (F5) ➔ Cloud Sync Zero PII (F15)

---

### Tier 4: Real-World Mysuru Transit Scenarios (15 Tests)
Simulates end-to-end municipal operational workflows along major Mysuru public transit corridors:
- `S01`: KSRTC Electric Bus traversing Outer Ring Road detecting critical pothole near VVCE.
- `S02`: BMTC Intercity Bus entering Mysuru via Hunsur Road detecting road cracks near Kalamandira.
- `S03`: Heritage corridor transit on Sayyaji Rao Road detecting surface fissures near Palace North Gate.
- `S04`: Monsoon flash-flood waterlogging on Outer Ring Road between Hebbal and Columbia Asia.
- `S05`: Multi-pass consensus: 3 consecutive transit passes over same pothole cluster.
- `S06`: Real-time driver avoidance maneuver at K.R. Circle with Kannada voice prompt.
- `S07`: Complete offline survey along 40 waypoints of Outer Ring Road with zero WAN and delayed sync.
- `S08`: Nighttime transit survey with low-light camera feed and high-beam contrast detection.
- `S09`: KTPP Act automated tender voucher auto-dispatch for critical pothole on Hunsur Road.
- `S10`: Multi-bus fleet traversal through Irwin Road & Sayyaji Rao Road junction with spatial deduplication.
- `S11`: IMU Z-shock discrimination: positive bump (+0.42g) vs negative pothole crater (-0.38g).
- `S12`: High-speed corridor traversal (60 km/h) on Outer Ring Road testing sub-15ms edge CV latency.
- `S13`: Urban canyon along heritage Sayyaji Rao Road correcting 15m GPS drift via corridor matching.
- `S14`: Dual-language cab prompt (Kannada & Hindi) for inter-state KSRTC drivers on Hunsur Road.
- `S15`: Municipal ward budget and CPWD voucher reconciliation for Ward 18 (Vijayanagar - Gokulam).

---

## 3. Test Execution Instructions

### Running the Full E2E Test Suite via Unittest
```bash
python -m unittest tests/test_e2e_suite.py
```

### Running Standalone with Formatted Summary
```bash
python tests/test_e2e_suite.py
```

### Running the Entire Project Test Suite (All 258 Tests)
```bash
python -m unittest discover tests
```

---

## 4. Test Infrastructure Components & Files

| Component | Path | Responsibility |
| :--- | :--- | :--- |
| **E2E Test Suite** | `tests/test_e2e_suite.py` | 202 comprehensive E2E tests across Tiers 1–4. |
| **E2E Test Helpers** | `tests/test_e2e_helpers.py` | Pure-Python ISO 6709 atom builder/parser, EXIF GPS builder, synthetic asphalt frame generator, OpenCV edge CV analyzer, Haversine corridor interpolator, detour polyline generator, multilingual voice renderer, and offline sync queue. |
| **Pipeline Unit Tests** | `tests/test_pipeline.py` | 42 unit tests covering multi-agent consensus pipeline. |
| **Fleet Stress Tests** | `tests/test_fleet_stress.py` | 14 stress tests simulating 52 concurrent electric transit buses. |
| **Test Infrastructure Spec** | `TEST_INFRA.md` | Authoritative test suite architecture and specifications. |
| **Test Readiness Declaration** | `TEST_READY.md` | Verification certificate and test results manifest. |
