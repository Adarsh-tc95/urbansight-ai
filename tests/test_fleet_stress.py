"""
UrbanSight AI — Fleet Stress Simulation & Consensus Engine Unit & Integration Test Suite
Infothon 7.0 · Problem Statement #07 · SIH26124

Verifies:
  1. Fleet Initialization & Corridor Coverage (50+ KSRTC & BMTC Electric Buses across Mysuru & Bengaluru)
  2. Agent 1: Vision Perception throughput, confidence gating (<0.70 rejection), and DPDP §2(t) redaction
  3. Agent 2: DBSCAN Spatial Deduplication within 15-30m and IMU shock consensus (speed bump rejection)
  4. Agent 3: Autonomous Municipal Dispatcher consensus, CPWD SOR costing throughput, and deduplication
  5. Agent 4: In-Cab Fleet Driver Advisory broadcasting within 300m horizon
  6. End-to-End Concurrent Multi-Threaded Fleet Stress Simulation Pipeline
  7. Benchmark Report Generation & Formatting
"""

import sys
import os
import unittest
import tempfile
import random

# Ensure urbansight-ai is at the head of sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT in sys.path:
    sys.path.remove(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

from backend.models import (
    HazardType, SeverityLevel, TicketStatus,
    HazardDetection, PWDWorkOrder, DriverAdvisory,
    BusTelemetry
)
from backend.agents.vision_perception import (
    VisionPerceptionAgent, LowConfidenceError, RDD_CODE_MAPPING
)
from backend.agents.geospatial_cluster import (
    GeospatialClusteringAgent, haversine_distance_meters
)
from backend.agents.municipal_dispatcher import (
    MunicipalDispatcherAgent, CPWD_SOR_REGISTRY
)
from backend.agents.fleet_advisory import (
    FleetAdvisoryAgent, MAX_ADVISORY_DISTANCE_METERS
)
from distributed.fleet_stress_simulation import (
    build_electric_bus_fleet, CORRIDOR_WAYPOINTS,
    ThreadSafeStressOrchestrator, FleetStressSimulator,
    DetectionTelemetryEvent, generate_markdown_report,
    calculate_percentile
)


class TestFleetInitializationAndCorridors(unittest.TestCase):
    """Verifies fleet scaling (50+ electric transit buses) and corridor geometries."""

    def test_fleet_scale_and_composition(self):
        """Validates at least 50 electric buses with dual-operator distribution."""
        fleet = build_electric_bus_fleet()
        self.assertGreaterEqual(len(fleet), 50, "Fleet must scale to 50+ electric transit buses.")
        self.assertEqual(len(fleet), 52)

        ksrtc_buses = [b for b in fleet if b.operator == "KSRTC"]
        bmtc_buses = [b for b in fleet if b.operator == "BMTC"]

        self.assertEqual(len(ksrtc_buses), 26, "Must instantiate 26 KSRTC electric buses.")
        self.assertEqual(len(bmtc_buses), 26, "Must instantiate 26 BMTC electric buses.")

        for bus in fleet:
            self.assertTrue(bus.bus_id.startswith("BMTC-") or bus.bus_id.startswith("KSRTC-"))
            self.assertEqual(bus.camera_status, "ONLINE_30FPS")
            self.assertTrue(bus.privacy_blur_active)
            self.assertGreater(bus.lat, 0.0)
            self.assertGreater(bus.lng, 0.0)

    def test_corridor_coverage(self):
        """Validates all 6 required corridors across Mysuru and Bengaluru are represented."""
        expected_corridors = [
            "MYSURU_OUTER_RING_ROAD",
            "MYSURU_HUNSUR_ROAD",
            "MYSURU_SAYYAJI_RAO_ROAD",
            "BENGALURU_SILK_BOARD",
            "BENGALURU_BELLANDUR",
            "BENGALURU_MARATHAHALLI"
        ]
        for c_key in expected_corridors:
            self.assertIn(c_key, CORRIDOR_WAYPOINTS)
            wps = CORRIDOR_WAYPOINTS[c_key]
            self.assertGreater(len(wps), 0, f"Corridor {c_key} must contain waypoints.")

            # Check geographic bounds: Mysuru ~ 12.25-12.40 lat, Bengaluru ~ 12.80-13.10 lat
            if "MYSURU" in c_key:
                for wp in wps:
                    self.assertTrue(12.20 <= wp.lat <= 12.45, f"Mysuru latitude out of range: {wp.lat}")
                    self.assertTrue(76.50 <= wp.lng <= 76.75, f"Mysuru longitude out of range: {wp.lng}")
            elif "BENGALURU" in c_key:
                for wp in wps:
                    self.assertTrue(12.80 <= wp.lat <= 13.15, f"Bengaluru latitude out of range: {wp.lat}")
                    self.assertTrue(77.55 <= wp.lng <= 77.80, f"Bengaluru longitude out of range: {wp.lng}")


class TestAgent1VisionPerceptionUnderLoad(unittest.TestCase):
    """Stress-tests Agent 1 Vision Perception: throughput, confidence gating, and DPDP privacy."""

    def setUp(self):
        self.agent = VisionPerceptionAgent(min_confidence=0.70)

    def test_confidence_gating_under_load(self):
        """Verifies strict confidence gating: >= 0.70 accepted, < 0.70 rejected."""
        # Valid confidence
        res = self.agent.detect(
            bus_id="BMTC-KA57-E901",
            hazard_type=HazardType.POTHOLE,
            lat=12.9172,
            lng=77.6228,
            location_name="Silk Board Flyover",
            confidence=0.92
        )
        self.assertIsNotNone(res)
        self.assertEqual(res["hazard_type"], HazardType.POTHOLE)
        self.assertEqual(res["rdd_code"], "D40 (Pothole / Subsidence)")

        # Low confidence (< 0.70) must raise LowConfidenceError
        low_confs = [0.69, 0.65, 0.50, 0.35, 0.10]
        for c in low_confs:
            with self.assertRaises(LowConfidenceError):
                self.agent.detect(
                    bus_id="BMTC-KA57-E901",
                    hazard_type=HazardType.POTHOLE,
                    lat=12.9172,
                    lng=77.6228,
                    location_name="Silk Board Flyover",
                    confidence=c
                )

    def test_dpdp_privacy_compliance(self):
        """Verifies in-memory volatile DPDP Act 2023 §2(t) redaction."""
        res = self.agent.detect(
            bus_id="KSRTC-KA09-EV01",
            hazard_type=HazardType.ROAD_CRACK,
            lat=12.3360,
            lng=76.6210,
            location_name="VVCE Gokulam Campus",
            confidence=0.88,
            enable_dpdp=True
        )
        privacy = res["privacy"]
        self.assertTrue(privacy["dpdp_compliant"])
        self.assertTrue(privacy["zero_storage_persistence"])
        self.assertTrue(privacy["volatile_ram_discarded"])
        self.assertEqual(privacy["section"], "DPDP Act 2023 §2(t)")
        self.assertTrue(privacy["audit_token"].startswith("DPDP-AUDIT-"))

    def test_physical_distress_severity_mapping(self):
        """Verifies physical distress metrics and severity level classification."""
        # Deep pothole >= 8.0 cm -> CRITICAL_P1
        sev, distress = self.agent.estimate_physical_distress(
            hazard_type=HazardType.POTHOLE,
            damage_depth_cm=9.5
        )
        self.assertEqual(sev, SeverityLevel.CRITICAL_P1)
        self.assertEqual(distress["depth_cm"], 9.5)

        # Shallow pothole < 4.0 cm -> MEDIUM_P3
        sev, distress = self.agent.estimate_physical_distress(
            hazard_type=HazardType.POTHOLE,
            damage_depth_cm=3.2
        )
        self.assertEqual(sev, SeverityLevel.MEDIUM_P3)

        # Long crack >= 20.0 m -> HIGH_P2
        sev, distress = self.agent.estimate_physical_distress(
            hazard_type=HazardType.ROAD_CRACK,
            affected_length_m=25.0
        )
        self.assertEqual(sev, SeverityLevel.HIGH_P2)


class TestAgent2SpatialDBSCANAndIMUUnderLoad(unittest.TestCase):
    """Stress-tests Agent 2 Geo-Spatial Clustering & IMU Sensor Fusion."""

    def setUp(self):
        self.clustering_agent = GeospatialClusteringAgent(epsilon_meters=25.0)

    def test_dbscan_spatial_clustering_multi_pass(self):
        """Verifies that 10 repeat passes at the same spot merge into 1 canonical cluster."""
        base_lat = 12.9172
        base_lng = 77.6228
        existing_hazards: List[HazardDetection] = []

        # 1st pass: creates new cluster
        data_1 = {
            "bus_id": "BMTC-KA57-E901",
            "hazard_type": HazardType.POTHOLE,
            "lat": base_lat,
            "lng": base_lng,
            "location_name": "Silk Board Junction",
            "confidence": 0.92,
            "damage_depth_cm": 8.5
        }
        hazard, is_new, msg = self.clustering_agent.cluster_detection(
            detection_data=data_1,
            existing_hazards=existing_hazards,
            z_shock=-0.38
        )
        self.assertTrue(is_new)
        self.assertEqual(len(existing_hazards), 1)
        self.assertEqual(hazard.pass_count, 1)

        # 9 subsequent passes from other buses within ~10m jitter
        for i in range(2, 11):
            jitter_lat = base_lat + (random.random() - 0.5) * 0.0001
            jitter_lng = base_lng + (random.random() - 0.5) * 0.0001
            data_next = {
                "bus_id": f"BMTC-KA57-E9{i:02d}",
                "hazard_type": HazardType.POTHOLE,
                "lat": jitter_lat,
                "lng": jitter_lng,
                "location_name": "Silk Board Junction",
                "confidence": 0.95,
                "damage_depth_cm": 9.2
            }
            c_haz, is_new_repeat, msg_repeat = self.clustering_agent.cluster_detection(
                detection_data=data_next,
                existing_hazards=existing_hazards,
                z_shock=-0.42
            )
            self.assertFalse(is_new_repeat, f"Pass {i} should be merged into existing cluster.")
            self.assertEqual(len(existing_hazards), 1, "Should not create duplicate clusters.")
            self.assertEqual(c_haz.pass_count, i)
            self.assertEqual(c_haz.damage_depth_cm, 9.2)

    def test_imu_shock_false_positive_elimination(self):
        """Verifies physical IMU shock filter eliminates speed bump false alarms."""
        existing_hazards: List[HazardDetection] = []
        data = {
            "bus_id": "KSRTC-KA09-EV14",
            "hazard_type": HazardType.POTHOLE,
            "lat": 12.3120,
            "lng": 76.6300,
            "location_name": "Hunsur Road Speed Table",
            "confidence": 0.96,
            "damage_depth_cm": 4.0
        }

        # Upward shock (+az = +0.55g) -> speed bump -> must raise ValueError
        with self.assertRaises(ValueError) as ctx:
            self.clustering_agent.cluster_detection(
                detection_data=data,
                existing_hazards=existing_hazards,
                z_shock=+0.55
            )
        self.assertIn("speed bump", str(ctx.exception).lower())
        self.assertEqual(len(existing_hazards), 0, "Speed bump must never create a hazard node.")

        # Downward drop (-az = -0.40g) -> confirmed pothole void -> accepted
        haz, is_new, _ = self.clustering_agent.cluster_detection(
            detection_data=data,
            existing_hazards=existing_hazards,
            z_shock=-0.40
        )
        self.assertTrue(is_new)
        self.assertEqual(len(existing_hazards), 1)
        self.assertTrue(haz.imu_verified)


class TestAgent3MunicipalDispatcherAndCostingUnderLoad(unittest.TestCase):
    """Stress-tests Agent 3 Municipal Dispatcher: consensus evaluation and CPWD SOR costing."""

    def setUp(self):
        self.dispatcher = MunicipalDispatcherAgent()

    def test_consensus_evaluation_threshold(self):
        """Verifies dispatch rule: requires pass_count >= 2 OR CRITICAL_P1."""
        # Single pass on MEDIUM_P3 defect -> does not dispatch
        hazard_p3 = HazardDetection(
            id="HAZ-TEST-P3",
            bus_id="BMTC-1",
            hazard_type=HazardType.ROAD_CRACK,
            severity=SeverityLevel.MEDIUM_P3,
            confidence=0.85,
            lat=12.9260,
            lng=77.6765,
            location_name="Bellandur EcoSpace Main Arterial",
            pass_count=1
        )
        self.assertFalse(self.dispatcher.should_dispatch(hazard_p3))

        # Second pass (pass_count = 2) -> qualifies for dispatch
        hazard_p3.pass_count = 2
        self.assertTrue(self.dispatcher.should_dispatch(hazard_p3))

        # Single pass on CRITICAL_P1 defect -> immediate fast-track dispatch
        hazard_p1 = HazardDetection(
            id="HAZ-TEST-P1",
            bus_id="BMTC-2",
            hazard_type=HazardType.POTHOLE,
            severity=SeverityLevel.CRITICAL_P1,
            confidence=0.96,
            lat=12.9172,
            lng=77.6228,
            location_name="Silk Board Junction",
            pass_count=1
        )
        self.assertTrue(self.dispatcher.should_dispatch(hazard_p1))

    def test_work_order_deduplication(self):
        """Verifies an already dispatched hazard is never duplicate dispatched."""
        work_orders: List[PWDWorkOrder] = []
        hazard = HazardDetection(
            id="HAZ-DEDUP-01",
            bus_id="BMTC-1",
            hazard_type=HazardType.POTHOLE,
            severity=SeverityLevel.CRITICAL_P1,
            confidence=0.95,
            lat=12.9172,
            lng=77.6228,
            location_name="Silk Board Junction",
            pass_count=1
        )

        # 1st dispatch: succeeds
        wo1, disp1, _ = self.dispatcher.evaluate_and_dispatch(hazard, work_orders)
        self.assertTrue(disp1)
        self.assertIsNotNone(wo1)
        self.assertEqual(len(work_orders), 1)
        self.assertEqual(hazard.status, TicketStatus.AUTO_DISPATCHED)

        # 2nd attempt: idempotent (returns None, False)
        wo2, disp2, _ = self.dispatcher.evaluate_and_dispatch(hazard, work_orders)
        self.assertFalse(disp2)
        self.assertIsNone(wo2)
        self.assertEqual(len(work_orders), 1, "Work orders must not be duplicated.")

    def test_cpwd_sor_mapping_and_costing(self):
        """Verifies accurate CPWD Schedule of Rates code mapping and itemized costing."""
        sor_pothole = CPWD_SOR_REGISTRY[HazardType.POTHOLE]
        self.assertEqual(sor_pothole["sor_code"], "CPWD-16.14.2")
        self.assertEqual(sor_pothole["base_cost_inr"], 4200.0)

        # Generate tender voucher
        sample_wo = PWDWorkOrder(
            ticket_id="PWD-2026-OCT-1001",
            hazard_id="HAZ-TEST-001",
            hazard_type=HazardType.POTHOLE,
            severity=SeverityLevel.CRITICAL_P1,
            location_name="Silk Board Junction Flyover",
            lat=12.9172,
            lng=77.6228,
            cluster_count=5,
            sla_hours=24,
            cpwd_sor_code="CPWD-16.14.2",
            estimated_cost_inr=4200.0
        )
        voucher = self.dispatcher.generate_voucher_data(work_order=sample_wo)
        self.assertEqual(voucher["ticket_id"], "PWD-2026-OCT-1001")
        self.assertEqual(voucher["cpwd_sor_code"], "CPWD-16.14.2")
        self.assertEqual(voucher["subtotal_inr"], 4200.0)
        self.assertEqual(voucher["gst_amount_inr"], round(4200.0 * 0.18, 2))
        self.assertEqual(voucher["total_sanction_inr"], round(4200.0 * 1.18, 2))
        self.assertIn("boq_items", voucher)
        self.assertGreater(len(voucher["boq_items"]), 0)


class TestAgent4FleetInCabAdvisoryUnderLoad(unittest.TestCase):
    """Stress-tests Agent 4 Fleet Driver In-Cab Advisory broadcasting."""

    def setUp(self):
        self.advisory_agent = FleetAdvisoryAgent(max_horizon_m=300)

    def test_driver_advisory_tactical_guidance(self):
        """Verifies tactical lane merge and deceleration recommendations."""
        hazard = HazardDetection(
            id="HAZ-ADV-01",
            bus_id="BMTC-KA57-E901",
            hazard_type=HazardType.POTHOLE,
            severity=SeverityLevel.CRITICAL_P1,
            confidence=0.96,
            lat=12.9240,
            lng=77.6730,
            location_name="Bellandur Flyover Pillar 34"
        )
        adv = self.advisory_agent.generate_advisory(
            hazard=hazard,
            approaching_bus_id="BMTC-KA57-E902",
            distance_meters=85
        )
        self.assertEqual(adv.alert_level, "CRITICAL")
        self.assertEqual(adv.recommended_lane, "Left lane merge recommended")
        self.assertEqual(adv.speed_reduction_kmh, 20)
        self.assertIn("Left lane merge recommended", adv.recommendation)
        self.assertIn("85m", adv.recommendation)

    def test_fleet_proximity_scan_horizon(self):
        """Verifies that only buses within the 300m horizon receive advisories."""
        hazard = HazardDetection(
            id="HAZ-ADV-02",
            bus_id="BMTC-KA57-E901",
            hazard_type=HazardType.POTHOLE,
            severity=SeverityLevel.CRITICAL_P1,
            confidence=0.96,
            lat=12.9240,
            lng=77.6730,
            location_name="Bellandur Flyover Pillar 34"
        )
        # Bus 1: within 150m (~0.001 deg lat is ~111m)
        bus_near = BusTelemetry(
            bus_id="BMTC-NEAR-1",
            route_name="Route 500D",
            lat=12.9250,
            lng=77.6730,
            speed_kmh=35.0,
            heading_deg=180.0
        )
        # Bus 2: 3 km away (~0.03 deg lat)
        bus_far = BusTelemetry(
            bus_id="BMTC-FAR-1",
            route_name="Route 500D",
            lat=12.9550,
            lng=77.6730,
            speed_kmh=45.0,
            heading_deg=180.0
        )

        test_advisories = []
        advisories = self.advisory_agent.evaluate_fleet_proximity(
            hazard=hazard,
            buses=[bus_near, bus_far],
            advisories_list=test_advisories
        )

        # Only bus_near should have triggered an advisory
        self.assertEqual(len(advisories), 1)
        self.assertEqual(advisories[0].bus_id, "BMTC-NEAR-1")
        self.assertLessEqual(advisories[0].distance_meters, 300)


class TestConcurrentFleetStressSimulationEngine(unittest.TestCase):
    """End-to-end multi-threaded concurrent stress test on full fleet."""

    def test_full_concurrent_stress_simulation(self):
        """Runs full concurrent simulation with 52 buses and verifies benchmarks."""
        simulator = FleetStressSimulator(
            num_buses=52,
            passes_per_bus=10,
            concurrency_workers=16,
            low_confidence_rate=0.06,
            speed_bump_rate=0.05
        )

        result = simulator.run_stress_test()

        # 1. Fleet Scale Assertion
        self.assertEqual(result.total_buses, 52)
        self.assertEqual(result.ksrtc_buses, 26)
        self.assertEqual(result.bmtc_buses, 26)

        # 2. Ingestion & Gating Assertions
        self.assertGreaterEqual(result.raw_detections_generated, 500)
        self.assertGreater(result.agent1_valid_detections, 0)
        self.assertGreater(result.agent1_rejected_low_conf, 0)
        self.assertGreater(result.agent2_speed_bumps_rejected, 0)

        # 3. Deduplication & Dispatch Assertions
        self.assertGreater(result.agent2_clusters_formed, 0)
        self.assertGreater(result.agent2_repeat_passes_merged, 0)
        self.assertGreater(result.agent3_work_orders_filed, 0)
        self.assertGreater(result.agent4_advisories_broadcast, 0)
        self.assertGreaterEqual(result.dedup_ratio, 5.0, "Deduplication ratio must compress > 5:1.")
        self.assertGreaterEqual(result.bandwidth_saved_pct, 80.0, "Must achieve >80% bandwidth reduction.")

        # 4. Throughput & Latency Assertions
        self.assertGreater(result.overall_throughput_det_per_sec, 250.0, "Must sustain >250 det/sec concurrent throughput.")
        self.assertLess(result.p95_latency_ms, 50.0, "P95 latency must remain <50ms.")
        self.assertLess(result.agent1_mean_ms, 5.0)
        self.assertLess(result.agent2_mean_ms, 5.0)

        # 5. Resource Assertions
        self.assertLess(result.mem_peak_mb, 50.0, "Peak memory must remain <50 MB.")


class TestBenchmarkReportGeneration(unittest.TestCase):
    """Verifies markdown report generation."""

    def test_report_creation(self):
        """Validates STRESS_TEST_BENCHMARK_REPORT.md file generation and markdown structure."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_file = os.path.join(tmp_dir, "TEST_STRESS_REPORT.md")
            simulator = FleetStressSimulator(num_buses=50, passes_per_bus=5, concurrency_workers=8)
            res = simulator.run_stress_test()
            generate_markdown_report(res, out_file)

            self.assertTrue(os.path.exists(out_file))
            with open(out_file, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertIn("UrbanSight AI — Transit Fleet Stress Simulation", content)
            self.assertIn("Infothon 7.0 · Problem Statement #07 · SIH26124", content)
            self.assertIn("High-Throughput Performance & Latency Matrix", content)
            self.assertIn("Agent 1: Vision Perception", content)
            self.assertIn("Agent 2: Spatial DBSCAN", content)
            self.assertIn("Agent 3: Municipal Dispatch", content)
            self.assertIn("Agent 4: Fleet In-Cab HUD", content)
            self.assertIn("Conclusion & Production Readiness", content)


if __name__ == "__main__":
    unittest.main()
