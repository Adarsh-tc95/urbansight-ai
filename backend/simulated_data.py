"""
Realistic Indian city transit fleet simulation data for UrbanSight AI.
Centered on Bengaluru & Mysuru arterial transit networks.
"""

INITIAL_BUSES = [
    {
        "bus_id": "KSRTC-MY09-C330",
        "route_name": "Mysuru Ring Road Express (Chamundi ↔ Columbia Asia)",
        "lat": 12.3480,
        "lng": 76.6620,
        "speed_kmh": 42.0,
        "heading_deg": 270.0,
        "camera_status": "ONLINE_30FPS",
        "privacy_blur_active": True
    },
    {
        "bus_id": "BMTC-KA01-E542",
        "route_name": "Outer Ring Road Express (Silk Board ↔ Marathahalli)",
        "lat": 12.9238,
        "lng": 77.6745,
        "speed_kmh": 24.5,
        "heading_deg": 45.0,
        "camera_status": "ONLINE_30FPS",
        "privacy_blur_active": True
    },
    {
        "bus_id": "BMTC-KA57-E912",
        "route_name": "Route 500D (Hebbal ↔ Electronic City)",
        "lat": 12.9112,
        "lng": 77.6380,
        "speed_kmh": 18.2,
        "heading_deg": 180.0,
        "camera_status": "ONLINE_30FPS",
        "privacy_blur_active": True
    },
    {
        "bus_id": "KSRTC-KA09-E102",
        "route_name": "Mysuru Ring Road (VVCE ↔ Infosys Campus)",
        "lat": 12.3160,
        "lng": 76.6413,
        "speed_kmh": 32.0,
        "heading_deg": 90.0,
        "camera_status": "ONLINE_30FPS",
        "privacy_blur_active": True
    },
    {
        "bus_id": "BMTC-KA03-E304",
        "route_name": "Majestic ↔ Whitefield ITPL Corridor",
        "lat": 12.9716,
        "lng": 77.5946,
        "speed_kmh": 14.8,
        "heading_deg": 115.0,
        "camera_status": "ONLINE_30FPS",
        "privacy_blur_active": True
    },
    {
        "bus_id": "BMTC-KA04-E780",
        "route_name": "Kengeri ↔ Banashankari Feeder Route",
        "lat": 12.9165,
        "lng": 77.5340,
        "speed_kmh": 28.0,
        "heading_deg": 270.0,
        "camera_status": "ONLINE_30FPS",
        "privacy_blur_active": True
    }
]

INITIAL_HAZARDS = [
    {
        "id": "HAZ-2026-001",
        "bus_id": "BMTC-KA01-E542",
        "hazard_type": "POTHOLE",
        "severity": "CRITICAL_P1",
        "confidence": 0.964,
        "lat": 12.9250,
        "lng": 77.6760,
        "location_name": "Outer Ring Road near Bellandur Flyover Pillar 34",
        "damage_depth_cm": 9.4,
        "affected_length_m": 1.8,
        "pass_count": 14,
        "cluster_id": "DBSCAN-CL-041",
        "image_url": "image1.jpg",
        "status": "AUTO_DISPATCHED",
        "pwd_ticket_id": "PWD-2026-OCT-0941"
    },
    {
        "id": "HAZ-2026-002",
        "bus_id": "BMTC-KA57-E912",
        "hazard_type": "WATERLOGGING",
        "severity": "HIGH_P2",
        "confidence": 0.921,
        "lat": 12.9125,
        "lng": 77.6395,
        "location_name": "Silk Board Underpass South Lane",
        "damage_depth_cm": None,
        "affected_length_m": 35.0,
        "pass_count": 8,
        "cluster_id": "DBSCAN-CL-018",
        "image_url": "image1.jpg",
        "status": "AUTO_DISPATCHED",
        "pwd_ticket_id": "PWD-2026-OCT-0882"
    },
    {
        "id": "HAZ-2026-003",
        "bus_id": "KSRTC-KA09-E102",
        "hazard_type": "POTHOLE",
        "severity": "CRITICAL_P1",
        "confidence": 0.948,
        "lat": 12.3190,
        "lng": 76.6450,
        "location_name": "VVCE Ring Road Junction, Mysuru",
        "damage_depth_cm": 8.6,
        "affected_length_m": 2.1,
        "pass_count": 6,
        "cluster_id": "DBSCAN-CL-009",
        "image_url": "image1.jpg",
        "status": "AUTO_DISPATCHED",
        "pwd_ticket_id": "PWD-2026-OCT-0715"
    },
    {
        "id": "HAZ-2026-004",
        "bus_id": "BMTC-KA03-E304",
        "hazard_type": "CONGESTION",
        "severity": "MEDIUM_P3",
        "confidence": 0.885,
        "lat": 12.9730,
        "lng": 77.5960,
        "location_name": "Kasturba Road Bottleneck (Speed: 9 km/h)",
        "damage_depth_cm": None,
        "affected_length_m": 450.0,
        "pass_count": 12,
        "cluster_id": "DBSCAN-CL-055",
        "image_url": "image2.jpg",
        "status": "CLUSTERED",
        "pwd_ticket_id": None
    },
    {
        "id": "HAZ-2026-005",
        "bus_id": "BMTC-KA04-E780",
        "hazard_type": "ROAD_CRACK",
        "severity": "LOW_P4",
        "confidence": 0.892,
        "lat": 12.9180,
        "lng": 77.5360,
        "location_name": "Banashankari 3rd Stage Main Arterial",
        "damage_depth_cm": 2.3,
        "affected_length_m": 12.0,
        "pass_count": 4,
        "cluster_id": "DBSCAN-CL-022",
        "image_url": "image1.jpg",
        "status": "DETECTED",
        "pwd_ticket_id": None
    }
]

INITIAL_WORK_ORDERS = [
    {
        "ticket_id": "PWD-2026-OCT-0941",
        "hazard_id": "HAZ-2026-001",
        "hazard_type": "POTHOLE",
        "severity": "CRITICAL_P1",
        "location_name": "Outer Ring Road near Bellandur Flyover Pillar 34",
        "lat": 12.9250,
        "lng": 77.6760,
        "cluster_count": 14,
        "sla_hours": 48,
        "dispatched_to": "BBMP Ward 150 / PWD Mahadevapura Division",
        "status": "AUTO_DISPATCHED",
        "created_at": "2026-10-07T14:10:00"
    },
    {
        "ticket_id": "PWD-2026-OCT-0882",
        "hazard_id": "HAZ-2026-002",
        "hazard_type": "WATERLOGGING",
        "severity": "HIGH_P2",
        "location_name": "Silk Board Underpass South Lane",
        "lat": 12.9125,
        "lng": 77.6395,
        "cluster_count": 8,
        "sla_hours": 24,
        "dispatched_to": "BBMP Stormwater Drain Division 2",
        "status": "CREW_ASSIGNED",
        "created_at": "2026-10-07T13:45:00"
    },
    {
        "ticket_id": "PWD-2026-OCT-0715",
        "hazard_id": "HAZ-2026-003",
        "hazard_type": "POTHOLE",
        "severity": "CRITICAL_P1",
        "location_name": "VVCE Ring Road Junction, Mysuru",
        "lat": 12.3190,
        "lng": 76.6450,
        "cluster_count": 6,
        "sla_hours": 48,
        "dispatched_to": "MCC Mysuru Engineering Ward 9",
        "status": "IN_PROGRESS",
        "created_at": "2026-10-07T12:30:00"
    }
]
