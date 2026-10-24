"""
UrbanSight AI — Comprehensive Test Suite (Infothon 7.0 / SIH26124)
Unit & End-to-End Consensus Pipeline Tests:
- Agent 1: Vision Perception (YOLOv8/v10 inference, RDD2022 codes, DPDP Act 2023 redaction, confidence gating)
- Agent 2: Geo-Spatial Clustering (DBSCAN 15-30m spatial deduplication, multi-pass consensus, IMU shock verification)
- Agent 3: Autonomous Municipal Dispatcher (CPWD Schedule of Rates, SLA compliance, jurisdiction routing)
- Agent 4: Fleet Driver In-Cab Advisory (Approaching hazard horizon <300m, lane merge recommendations, speed reductions)
- Orchestrator: Multi-Agent Consensus Flow (Agent 1 -> Agent 2 -> Agent 3 -> Agent 4)
"""

import unittest
from backend.models import (
    HazardType, SeverityLevel, TicketStatus, HazardDetection, PWDWorkOrder,
    DriverAdvisory, BusTelemetry
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
from backend.agents.orchestrator import UrbanSightOrchestrator


class TestVisionPerceptionAgent(unittest.TestCase):
    """Verifies edge vision inference, DPDP privacy, confidence gating, and physical distress estimation."""

    def setUp(self):
        self.agent = VisionPerceptionAgent(min_confidence=0.70)

    def test_defect_categories(self):
        """Validates all required defect categories and RDD codes."""
        categories = [
            HazardType.POTHOLE,
            HazardType.ROAD_CRACK,
            HazardType.WATERLOGGING,
            HazardType.CONGESTION,
            HazardType.ROAD_DEBRIS,
            HazardType.ACCIDENT
        ]
        for cat in categories:
            res = self.agent.detect(
                bus_id="BMTC-KA01-E542",
                hazard_type=cat,
                lat=12.9350,
                lng=77.6820,
                location_name="Sarjapur Road",
                confidence=0.92
            )
            self.assertIn("rdd_code", res)
            self.assertEqual(res["hazard_type"], cat)
            self.assertIn("damage_depth_cm", res)
            self.assertIn("privacy", res)
            self.assertTrue(res["privacy"]["dpdp_compliant"])

    def test_confidence_threshold_valid(self):
        """Verifies detections meeting or exceeding 0.70 confidence are accepted."""
        self.assertTrue(self.agent.validate_confidence(0.70))
        self.assertTrue(self.agent.validate_confidence(0.95))
        res = self.agent.detect(
            bus_id="BMTC-TEST-1",
            hazard_type=HazardType.POTHOLE,
            lat=12.9300,
            lng=77.6800,
            location_name="Test Loc",
            confidence=0.72
        )
        self.assertEqual(res["confidence"], 0.72)

    def test_confidence_threshold_rejection(self):
        """Verifies detections below 0.70 confidence are rejected."""
        self.assertFalse(self.agent.validate_confidence(0.69))
        self.assertFalse(self.agent.validate_confidence(0.45))
        with self.assertRaises(LowConfidenceError):
            self.agent.detect(
                bus_id="BMTC-TEST-2",
                hazard_type=HazardType.POTHOLE,
                lat=12.9300,
                lng=77.6800,
                location_name="Low Conf",
                confidence=0.65
            )

    def test_dpdp_privacy_redaction(self):
        """Verifies DPDP Act 2023 §2(t) in-memory zero-persistence redaction."""
        privacy_data = self.agent.simulate_dpdp_privacy_redaction()
        self.assertTrue(privacy_data["dpdp_compliant"])
        self.assertTrue(privacy_data["zero_storage_persistence"])
        self.assertTrue(privacy_data["volatile_ram_discarded"])
        self.assertEqual(privacy_data["faces_masked"], 2)
        self.assertEqual(privacy_data["plates_masked"], 1)
        self.assertIn("audit_token", privacy_data)

    def test_physical_distress_estimation(self):
        """Verifies depth/length/area calculations and severity mapping."""
        # Critical pothole (depth >= 8cm)
        sev, metrics = self.agent.estimate_physical_distress(
            hazard_type=HazardType.POTHOLE,
            damage_depth_cm=9.5
        )
        self.assertEqual(sev, SeverityLevel.CRITICAL_P1)
        self.assertEqual(metrics["depth_cm"], 9.5)
        self.assertGreater(metrics["area_sqm"], 0.5)

        # High P2 pothole (depth between 4cm and 8cm)
        sev_p2, _ = self.agent.estimate_physical_distress(
            hazard_type=HazardType.POTHOLE,
            damage_depth_cm=5.0
        )
        self.assertEqual(sev_p2, SeverityLevel.HIGH_P2)

        # Long road crack (>= 20m)
        sev_crack, m_crack = self.agent.estimate_physical_distress(
            hazard_type=HazardType.ROAD_CRACK,
            affected_length_m=25.0
        )
        self.assertEqual(sev_crack, SeverityLevel.HIGH_P2)
        self.assertEqual(m_crack["length_m"], 25.0)


class TestGeospatialClusteringAgent(unittest.TestCase):
    """Verifies DBSCAN spatial deduplication, pass counting, and IMU vibration verification."""

    def setUp(self):
        self.agent = GeospatialClusteringAgent(epsilon_meters=25.0)
        self.hazards_pool = []

    def test_new_canonical_cluster(self):
        """Verifies initial detection creates canonical cluster with pass_count=1."""
        det_data = {
            "bus_id": "BMTC-KA01-E542",
            "hazard_type": HazardType.POTHOLE,
            "severity": SeverityLevel.CRITICAL_P1,
            "confidence": 0.94,
            "lat": 12.9350,
            "lng": 77.6820,
            "location_name": "Sarjapur ORR",
            "damage_depth_cm": 9.0
        }
        hazard, is_new, msg = self.agent.cluster_detection(det_data, self.hazards_pool)
        self.assertTrue(is_new)
        self.assertEqual(hazard.pass_count, 1)
        self.assertIn("DBSCAN-CL-", hazard.cluster_id)
        self.assertEqual(len(self.hazards_pool), 1)

    def test_multipass_spatial_deduplication(self):
        """Verifies subsequent detection within ~15-25m is merged, incrementing pass_count."""
        # Initial pass at (12.93500, 77.68200)
        det_1 = {
            "bus_id": "BMTC-KA01-E542",
            "hazard_type": HazardType.POTHOLE,
            "severity": SeverityLevel.HIGH_P2,
            "confidence": 0.90,
            "lat": 12.93500,
            "lng": 77.68200,
            "location_name": "Sarjapur ORR",
            "damage_depth_cm": 6.0
        }
        hazard_1, is_new_1, _ = self.agent.cluster_detection(det_1, self.hazards_pool)
        self.assertTrue(is_new_1)
        self.assertEqual(hazard_1.pass_count, 1)

        # 2nd pass from another bus ~12m away (delta ~0.0001 deg lat is ~11.1m)
        det_2 = {
            "bus_id": "BMTC-KA57-E912",
            "hazard_type": HazardType.POTHOLE,
            "severity": SeverityLevel.HIGH_P2,
            "confidence": 0.96,
            "lat": 12.93509,
            "lng": 77.68205,
            "location_name": "Sarjapur ORR",
            "damage_depth_cm": 7.5
        }
        hazard_2, is_new_2, msg_2 = self.agent.cluster_detection(det_2, self.hazards_pool)
        self.assertFalse(is_new_2)
        self.assertEqual(hazard_2.id, hazard_1.id)
        self.assertEqual(hazard_2.cluster_id, hazard_1.cluster_id)
        self.assertEqual(hazard_2.pass_count, 2)
        self.assertEqual(len(self.hazards_pool), 1)  # Deduplicated into 1 canonical node
        self.assertEqual(hazard_2.damage_depth_cm, 7.5)  # Updated to max distress
        self.assertGreaterEqual(hazard_2.confidence, 0.92)  # Running average updated

    def test_cluster_separation_beyond_epsilon(self):
        """Verifies detections outside epsilon form separate canonical clusters."""
        det_1 = {
            "bus_id": "BUS-1",
            "hazard_type": HazardType.POTHOLE,
            "severity": SeverityLevel.HIGH_P2,
            "confidence": 0.92,
            "lat": 12.9350,
            "lng": 77.6820,
            "location_name": "Location A"
        }
        self.agent.cluster_detection(det_1, self.hazards_pool)

        # 500 meters away
        det_2 = {
            "bus_id": "BUS-2",
            "hazard_type": HazardType.POTHOLE,
            "severity": SeverityLevel.HIGH_P2,
            "confidence": 0.91,
            "lat": 12.9395,
            "lng": 77.6820,
            "location_name": "Location B"
        }
        hazard_2, is_new_2, _ = self.agent.cluster_detection(det_2, self.hazards_pool)
        self.assertTrue(is_new_2)
        self.assertEqual(len(self.hazards_pool), 2)

    def test_imu_vibration_pothole_confirmed(self):
        """Verifies downward freefall (-az shock) confirms pothole void."""
        res = self.agent.verify_imu_vibration(HazardType.POTHOLE, z_shock=-0.65)
        self.assertTrue(res["verified"])
        self.assertFalse(res["is_false_positive"])
        self.assertEqual(res["classification"], "CONFIRMED_POTHOLE_VOID")

    def test_imu_vibration_speedbump_rejected(self):
        """Verifies upward heave (+az shock) rejects speed bump false alarm."""
        res = self.agent.verify_imu_vibration(HazardType.POTHOLE, z_shock=0.55)
        self.assertFalse(res["verified"])
        self.assertTrue(res["is_false_positive"])
        self.assertEqual(res["classification"], "SPEED_BUMP_FALSE_ALARM")

        # Ingesting with speed bump shock raises ValueError
        det_data = {
            "bus_id": "BUS-1",
            "hazard_type": HazardType.POTHOLE,
            "lat": 12.9350,
            "lng": 77.6820,
            "confidence": 0.95
        }
        with self.assertRaises(ValueError):
            self.agent.cluster_detection(det_data, self.hazards_pool, z_shock=0.60)


class TestMunicipalDispatcherAgent(unittest.TestCase):
    """Verifies PWD work-order auto-filing, CPWD SOR codes, SLA enforcement, and jurisdiction routing."""

    def setUp(self):
        self.agent = MunicipalDispatcherAgent()
        self.work_orders = []

    def test_p1_immediate_dispatch(self):
        """Verifies CRITICAL_P1 auto-files immediately on pass 1."""
        hazard = HazardDetection(
            id="HAZ-TEST-001",
            bus_id="BMTC-KA01-E542",
            hazard_type=HazardType.POTHOLE,
            severity=SeverityLevel.CRITICAL_P1,
            confidence=0.98,
            lat=12.9250,
            lng=77.6760,
            location_name="Bellandur Flyover Outer Ring Road",
            pass_count=1,
            status=TicketStatus.DETECTED
        )
        self.assertTrue(self.agent.should_dispatch(hazard))
        wo, dispatched, msg = self.agent.evaluate_and_dispatch(hazard, self.work_orders)
        self.assertTrue(dispatched)
        self.assertIsNotNone(wo)
        self.assertEqual(wo.sla_hours, 24)
        self.assertEqual(wo.cpwd_sor_code, "CPWD-16.14.2")
        self.assertEqual(hazard.status, TicketStatus.AUTO_DISPATCHED)
        self.assertIsNotNone(hazard.pwd_ticket_id)
        self.assertEqual(len(self.work_orders), 1)

    def test_multipass_consensus_dispatch(self):
        """Verifies HIGH_P2 waits for pass_count >= 2 before filing work order."""
        hazard = HazardDetection(
            id="HAZ-TEST-002",
            bus_id="BMTC-KA57-E912",
            hazard_type=HazardType.ROAD_CRACK,
            severity=SeverityLevel.HIGH_P2,
            confidence=0.88,
            lat=12.9125,
            lng=77.6395,
            location_name="Silk Board Corridor",
            pass_count=1,
            status=TicketStatus.DETECTED
        )
        # Pass 1: Should not dispatch
        self.assertFalse(self.agent.should_dispatch(hazard))
        wo1, dispatched1, _ = self.agent.evaluate_and_dispatch(hazard, self.work_orders)
        self.assertFalse(dispatched1)
        self.assertIsNone(wo1)
        self.assertEqual(len(self.work_orders), 0)

        # Pass 2: Reaches multi-pass consensus
        hazard.pass_count = 2
        self.assertTrue(self.agent.should_dispatch(hazard))
        wo2, dispatched2, _ = self.agent.evaluate_and_dispatch(hazard, self.work_orders)
        self.assertTrue(dispatched2)
        self.assertIsNotNone(wo2)
        self.assertEqual(wo2.sla_hours, 48)
        self.assertEqual(wo2.cpwd_sor_code, "CPWD-16.12.1")
        self.assertEqual(len(self.work_orders), 1)

    def test_jurisdiction_assignment(self):
        """Verifies accurate jurisdiction routing for BBMP wards and MCC Mysuru."""
        juris_orr = self.agent.resolve_jurisdiction("Outer Ring Road Bellandur", 12.9250, 77.6760)
        self.assertIn("Mahadevapura", juris_orr)

        juris_silk = self.agent.resolve_jurisdiction("Silk Board Underpass", 12.9125, 77.6395)
        self.assertIn("South Division", juris_silk)

        juris_mysuru = self.agent.resolve_jurisdiction("VVCE Ring Road Junction, Mysuru", 12.3190, 76.6450)
        self.assertIn("MCC Mysuru", juris_mysuru)

    def test_cpwd_sor_mapping(self):
        """Verifies distress to CPWD Schedule of Rates code mapping."""
        self.assertEqual(CPWD_SOR_REGISTRY[HazardType.POTHOLE]["sor_code"], "CPWD-16.14.2")
        self.assertEqual(CPWD_SOR_REGISTRY[HazardType.ROAD_CRACK]["sor_code"], "CPWD-16.12.1")
        self.assertEqual(CPWD_SOR_REGISTRY[HazardType.WATERLOGGING]["sor_code"], "CPWD-16.15.1")
        self.assertEqual(CPWD_SOR_REGISTRY[HazardType.CONGESTION]["sor_code"], "CPWD-16.08.3")
        self.assertEqual(CPWD_SOR_REGISTRY[HazardType.ROAD_DEBRIS]["sor_code"], "CPWD-16.03.4")
        self.assertEqual(CPWD_SOR_REGISTRY[HazardType.ACCIDENT]["sor_code"], "CPWD-16.01.0")

    def test_sla_enforcement(self):
        """Verifies SLA standards: <24h (P1), <48h (P2), <72h (P3)."""
        self.assertEqual(self.agent.compute_sla_hours(SeverityLevel.CRITICAL_P1), 24)
        self.assertEqual(self.agent.compute_sla_hours(SeverityLevel.HIGH_P2), 48)
        self.assertEqual(self.agent.compute_sla_hours(SeverityLevel.MEDIUM_P3), 72)
        self.assertEqual(self.agent.compute_sla_hours(SeverityLevel.LOW_P4), 120)

    def test_generate_voucher_data(self):
        """Verifies itemized CPWD SOR cost calculation, GST 18%, and penalty SLA clauses."""
        hazard = HazardDetection(
            id="HAZ-VOUCHER-1",
            bus_id="BUS-TEST",
            hazard_type=HazardType.POTHOLE,
            severity=SeverityLevel.CRITICAL_P1,
            confidence=0.97,
            lat=12.9250,
            lng=77.6760,
            location_name="Bellandur ORR"
        )
        wo = self.agent.generate_work_order(hazard)
        voucher = self.agent.generate_voucher_data(ticket_id=wo.ticket_id, work_order=wo)

        self.assertEqual(voucher["ticket_id"], wo.ticket_id)
        self.assertEqual(voucher["cpwd_sor_code"], "CPWD-16.14.2")
        self.assertEqual(len(voucher["line_items"]), 3)
        self.assertAlmostEqual(voucher["subtotal_inr"], 4200.0, places=1)
        self.assertAlmostEqual(voucher["gst_amount_inr"], round(4200.0 * 0.18, 2), places=1)
        self.assertAlmostEqual(voucher["total_estimated_inr"], round(4200.0 * 1.18, 2), places=1)
        self.assertIn("<24 hours", voucher["penalty_clause"])
        self.assertIn("CPWD Works Manual Section 29.3", voucher["penalty_clause"])
        self.assertTrue(voucher["verification_checksum"].startswith("CPWD-"))
    def test_voucher_data_generation(self):
        """Verifies itemized CPWD SOR voucher generation for official municipal tenders."""
        wo = PWDWorkOrder(
            ticket_id="PWD-TEST-001",
            hazard_id="HAZ-TEST-001",
            hazard_type=HazardType.POTHOLE,
            severity=SeverityLevel.CRITICAL_P1,
            location_name="Bellandur Flyover",
            lat=12.9250,
            lng=77.6760,
            cluster_count=14,
            sla_hours=24,
            dispatched_to="BBMP Mahadevapura Ward 85",
            status=TicketStatus.AUTO_DISPATCHED,
            cpwd_sor_code="CPWD-16.14.2",
            estimated_cost_inr=2190.0
        )
        voucher = self.agent.generate_voucher_data(wo)
        self.assertEqual(voucher["ticket_id"], "PWD-TEST-001")
        self.assertIn("boq_items", voucher)
        self.assertEqual(voucher["subtotal_inr"], 2190.0)
        self.assertEqual(voucher["gst_rate_percent"], 18.0)
        self.assertAlmostEqual(voucher["total_sanction_inr"], 2584.20, places=2)



class TestFleetAdvisoryAgent(unittest.TestCase):
    """Verifies driver in-cab advisory alerts, horizon gating (<300m), and tactical maneuver guidance."""

    def setUp(self):
        self.agent = FleetAdvisoryAgent(max_horizon_m=300)
        self.advisories = []

    def test_advisory_generation(self):
        """Verifies advisory payload creation for approaching transit vehicles."""
        hazard = HazardDetection(
            id="HAZ-ADV-1",
            bus_id="BMTC-KA01-E542",
            hazard_type=HazardType.POTHOLE,
            severity=SeverityLevel.CRITICAL_P1,
            confidence=0.96,
            lat=12.9350,
            lng=77.6820,
            location_name="Sarjapur-ORR Junction",
            status=TicketStatus.DETECTED
        )
        adv = self.agent.generate_advisory(
            hazard=hazard,
            approaching_bus_id="BMTC-KA01-E542",
            distance_meters=180,
            advisories_list=self.advisories
        )
        self.assertEqual(adv.bus_id, "BMTC-KA01-E542")
        self.assertEqual(adv.hazard_type, HazardType.POTHOLE)
        self.assertEqual(adv.alert_level, "CRITICAL")
        self.assertIn("Left lane merge", adv.recommendation)
        self.assertEqual(adv.speed_reduction_kmh, 20)
        self.assertEqual(len(self.advisories), 1)

    def test_alert_levels(self):
        """Verifies warning levels (CRITICAL, WARNING, INFO)."""
        self.assertEqual(self.agent.compute_alert_level(SeverityLevel.CRITICAL_P1, 180), "CRITICAL")
        self.assertEqual(self.agent.compute_alert_level(SeverityLevel.HIGH_P2, 90), "CRITICAL")  # <=100m
        self.assertEqual(self.agent.compute_alert_level(SeverityLevel.HIGH_P2, 200), "WARNING")
        self.assertEqual(self.agent.compute_alert_level(SeverityLevel.MEDIUM_P3, 280), "INFO")

    def test_tactical_recommendations(self):
        """Verifies lane merge advice and speed reduction across defect types."""
        lane, speed_red, _ = self.agent.compute_recommendations(HazardType.WATERLOGGING, SeverityLevel.HIGH_P2)
        self.assertIn("Center lane", lane)
        self.assertGreaterEqual(speed_red, 15)

        lane_acc, speed_acc, _ = self.agent.compute_recommendations(HazardType.ACCIDENT, SeverityLevel.CRITICAL_P1)
        self.assertIn("Extreme left lane", lane_acc)
        self.assertGreaterEqual(speed_acc, 20)


class TestEndToEndPipelineOrchestrator(unittest.TestCase):
    """Verifies full 4-agent consensus flow through the UrbanSight Orchestrator."""

    def setUp(self):
        self.orch = UrbanSightOrchestrator()

    def test_orchestrator_initial_state(self):
        """Verifies initial bootstrap state with online buses, seed hazards, and agent logs."""
        self.assertGreaterEqual(len(self.orch.buses), 4)
        self.assertGreaterEqual(len(self.orch.hazards), 5)
        self.assertGreaterEqual(len(self.orch.work_orders), 3)
        self.assertGreaterEqual(len(self.orch.event_logs), 4)
        metrics = self.orch.get_system_metrics()
        self.assertEqual(metrics["privacy_compliance"], "100% DPDP Act 2023 §2(t) Compliant (Zero PII)")
        self.assertIn("total_hazards_tracked", metrics)

    def test_e2e_critical_p1_consensus_flow(self):
        """
        Executes end-to-end consensus for a new Critical P1 pothole:
        Agent 1 (Vision) -> Agent 2 (DBSCAN) -> Agent 3 (PWD Auto-dispatch) -> Agent 4 (Advisory).
        """
        initial_hazard_count = len(self.orch.hazards)
        initial_wo_count = len(self.orch.work_orders)
        initial_adv_count = len(self.orch.advisories)

        # Fresh critical pothole detection on Sarjapur road
        det = self.orch.process_edge_detection(
            bus_id="BMTC-KA01-E542",
            hazard_type=HazardType.POTHOLE,
            lat=12.9388,
            lng=77.6855,
            location_name="Sarjapur Road Wipro Gate",
            confidence=0.965,
            damage_depth_cm=10.2,
            z_shock=-0.75  # Downward freefall confirmed by IMU
        )

        # 1. Agent 1 & Agent 2 verification: new canonical cluster
        self.assertEqual(len(self.orch.hazards), initial_hazard_count + 1)
        self.assertEqual(det.severity, SeverityLevel.CRITICAL_P1)
        self.assertEqual(det.pass_count, 1)
        self.assertTrue(det.imu_verified)

        # 2. Agent 3 verification: auto-dispatched PWD work order (CRITICAL_P1 immediately qualifies)
        self.assertEqual(det.status, TicketStatus.AUTO_DISPATCHED)
        self.assertIsNotNone(det.pwd_ticket_id)
        self.assertEqual(len(self.orch.work_orders), initial_wo_count + 1)
        new_wo = self.orch.work_orders[0]
        self.assertEqual(new_wo.ticket_id, det.pwd_ticket_id)
        self.assertEqual(new_wo.cpwd_sor_code, "CPWD-16.14.2")
        self.assertEqual(new_wo.sla_hours, 24)
        self.assertIn("Mahadevapura", new_wo.dispatched_to)

        # 3. Agent 4 verification: driver advisory broadcasted
        self.assertGreater(len(self.orch.advisories), initial_adv_count)
        new_adv = self.orch.advisories[0]
        self.assertEqual(new_adv.hazard_type, HazardType.POTHOLE)
        self.assertEqual(new_adv.alert_level, "CRITICAL")
        self.assertIn("Left lane merge", new_adv.recommendation)

    def test_e2e_multipass_deduplication_and_delayed_dispatch(self):
        """
        Executes multi-pass deduplication:
        Pass 1 (P2 crack): Form cluster, pass_count=1, no work order filed.
        Pass 2 (same crack ~10m delta): Merge cluster, pass_count=2, auto-files work order with CPWD-16.12.1.
        """
        initial_wo_count = len(self.orch.work_orders)

        # Pass 1 by Bus 1 (lat: 12.9500, lng: 77.6000)
        h1 = self.orch.process_edge_detection(
            bus_id="BMTC-KA03-E304",
            hazard_type=HazardType.ROAD_CRACK,
            lat=12.95000,
            lng=77.60000,
            location_name="Richmond Road Corridor",
            confidence=0.88,
            affected_length_m=12.0
        )
        self.assertEqual(h1.pass_count, 1)
        self.assertEqual(h1.severity, SeverityLevel.MEDIUM_P3)
        self.assertEqual(h1.status, TicketStatus.DETECTED)
        # No work order filed on pass 1 for MEDIUM_P3
        self.assertEqual(len(self.orch.work_orders), initial_wo_count)

        # Pass 2 by Bus 2 (~11m away)
        h2 = self.orch.process_edge_detection(
            bus_id="BMTC-KA04-E780",
            hazard_type=HazardType.ROAD_CRACK,
            lat=12.95008,
            lng=77.60005,
            location_name="Richmond Road Corridor",
            confidence=0.92,
            affected_length_m=14.0
        )
        self.assertEqual(h2.id, h1.id)
        self.assertEqual(h2.pass_count, 2)
        # Work order auto-filed on pass 2 consensus!
        self.assertEqual(h2.status, TicketStatus.AUTO_DISPATCHED)
        self.assertIsNotNone(h2.pwd_ticket_id)
        self.assertEqual(len(self.orch.work_orders), initial_wo_count + 1)
        self.assertEqual(self.orch.work_orders[0].cpwd_sor_code, "CPWD-16.12.1")


    def test_work_order_resolution_lifecycle(self):
        """Verifies work order lifecycle transition from AUTO_DISPATCHED -> IN_PROGRESS -> RESOLVED."""
        wo = self.orch.work_orders[0]
        self.assertIn(wo.status, [TicketStatus.AUTO_DISPATCHED, TicketStatus.CREW_ASSIGNED, TicketStatus.IN_PROGRESS])

        # Simulate field crew marking in progress
        wo.status = TicketStatus.IN_PROGRESS
        wo.assigned_crew_id = "CREW-VAN-04"
        self.assertEqual(wo.status, TicketStatus.IN_PROGRESS)

        # Simulate field crew resolving ticket
        wo.status = TicketStatus.RESOLVED
        wo.resolution_remarks = "Bituminous milling and DBM compaction certified."
        wo.resolved_at = "2026-10-23T08:20:00"

        self.assertEqual(wo.status, TicketStatus.RESOLVED)
        self.assertIsNotNone(wo.resolved_at)
        self.assertEqual(wo.assigned_crew_id, "CREW-VAN-04")


class TestPCIEngine(unittest.TestCase):
    """Verifies ASTM D6433 Pavement Condition Index (PCI) and Markov degradation decay forecasting."""

    def setUp(self):
        from backend.agents.pci_engine import PCIEngine
        self.pci = PCIEngine()

    def test_corridor_forecasts(self):
        corridors = self.pci.get_corridor_forecasts(days=0)
        self.assertGreater(len(corridors), 0)
        c0 = corridors[0]
        self.assertIn("projected_pci", c0)
        self.assertIn("rating_band", c0)
        self.assertIn("color", c0)

    def test_decay_progression(self):
        d0 = self.pci.get_corridor_forecasts(days=0)[0]["projected_pci"]
        d30 = self.pci.get_corridor_forecasts(days=30)[0]["projected_pci"]
        self.assertLess(d30, d0)

    def test_network_summary(self):
        summary = self.pci.get_network_governance_summary(days=0)
        self.assertIn("average_network_pci", summary)
        self.assertIn("economic_roi", summary)



class TestWardAnalytics(unittest.TestCase):
    """Verifies Municipal Ward Governance and Expenditure Analytics endpoint."""

    def test_ward_summary_endpoint(self):
        from backend.main import get_ward_analytics_summary
        data = get_ward_analytics_summary()
        self.assertIn("summary", data)
        self.assertIn("wards", data)
        self.assertIn("distress_breakdown", data)
        self.assertGreaterEqual(len(data["wards"]), 3)
        w0 = data["wards"][0]
        self.assertIn("ward_name", w0)
        self.assertIn("sla_compliance", w0)
        self.assertIn("grade", w0)
        self.assertGreaterEqual(w0["sla_compliance"], 90.0)


class TestMediaAnalysisPipeline(unittest.TestCase):
    """Verifies transit video and photo media analysis and end-to-end consensus trigger."""

    def test_media_analysis_json(self):
        from backend.main import analyze_media_json, MediaAnalysisRequest
        req = MediaAnalysisRequest(
            bus_id="KSRTC-KA09-E102",
            location_name="VVCE Ring Road Junction, Gokulam, Mysuru",
            lat=12.3360,
            lng=76.6210,
            hazard_type="POTHOLE",
            damage_depth_cm=8.9,
            media_name="dashcam_mysuru_orr.mp4"
        )
        res = analyze_media_json(req)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["media_type"], "VIDEO")
        self.assertTrue(res["hazard_detected"])
        self.assertIn("dpdp_privacy", res)
        self.assertTrue(res["dpdp_privacy"]["dpdp_compliant"])
        self.assertIn("work_order", res)
        self.assertTrue(res["work_order"]["ticket_id"].startswith("PWD-"))
        self.assertIn("bbox", res)
        self.assertEqual(res["defect"]["type"], "POTHOLE")
        self.assertAlmostEqual(res["defect"]["damage_depth_cm"], 8.9)


if __name__ == '__main__':
    unittest.main()
