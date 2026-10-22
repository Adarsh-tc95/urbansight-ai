"""
UrbanSight AI — Computer B Edge Bus Telemetry Generator
Simulates a moving transit bus fleet on Computer B streaming live hazard detections
and IMU vibration readings across the LAN to Computer A (Master Orchestrator).
"""

import time
import random
import requests
import argparse
from typing import Dict, Any

# Route coordinates along Bengaluru & Mysuru corridors
ROUTE_WAYPOINTS = [
    {"name": "Silk Board Junction Flyover Approach", "lat": 12.9172, "lng": 77.6228, "hazard": "POTHOLE", "depth": 9.4, "z_shock": -0.42},
    {"name": "Bellandur EcoSpace Main Arterial", "lat": 12.9260, "lng": 77.6765, "hazard": "ROAD_CRACK", "depth": 3.1, "z_shock": -0.15},
    {"name": "Marathahalli Underpass Lane 2", "lat": 12.9560, "lng": 77.7010, "hazard": "WATERLOGGING", "depth": None, "z_shock": None},
    {"name": "Tin Factory Junction Corridor", "lat": 12.9940, "lng": 77.6610, "hazard": "CONGESTION", "depth": None, "z_shock": None},
    {"name": "Kasturba Road Bottleneck", "lat": 12.9730, "lng": 77.5960, "hazard": "POTHOLE", "depth": 7.8, "z_shock": -0.38},
    {"name": "VVCE Ring Road Junction, Mysuru", "lat": 12.3190, "lng": 76.6450, "hazard": "POTHOLE", "depth": 8.6, "z_shock": -0.40},
    {"name": "Hunsur Road Speed Table (Speed Bump Check)", "lat": 12.3140, "lng": 76.6320, "hazard": "POTHOLE", "depth": 4.0, "z_shock": +0.55} # Will be rejected by IMU!
]

def stream_edge_telemetry(orchestrator_url: str, bus_id: str, interval_sec: float = 2.0, count: int = 20):
    print(f"================================================================")
    print(f"UrbanSight AI — Computer B Edge Sensing Node Starting")
    print(f"Target Master Orchestrator: {orchestrator_url}")
    print(f"Simulating Bus: {bus_id}")
    print(f"================================================================\n")

    for i in range(count):
        wp = random.choice(ROUTE_WAYPOINTS)
        # Add small jitter to simulate repeat passes for DBSCAN
        jitter_lat = wp["lat"] + (random.random() - 0.5) * 0.0001
        jitter_lng = wp["lng"] + (random.random() - 0.5) * 0.0001

        payload = {
            "bus_id": bus_id,
            "hazard_type": wp["hazard"],
            "lat": round(jitter_lat, 6),
            "lng": round(jitter_lng, 6),
            "location_name": wp["name"],
            "confidence": round(random.uniform(0.91, 0.98), 3),
            "damage_depth_cm": wp["depth"],
            "z_shock": wp["z_shock"]
        }

        try:
            start = time.perf_counter()
            resp = requests.post(
                f"{orchestrator_url}/api/simulate-detection",
                json=payload,
                timeout=5.0
            )
            elapsed_ms = (time.perf_counter() - start) * 1000

            if resp.status_code == 200:
                data = resp.json()
                detection = data.get("detection", {})
                print(f"[{i+1}/{count}] OK ({elapsed_ms:.1f}ms LAN): {wp['hazard']} @ {wp['name']} "
                      f"-> Cluster: {detection.get('cluster_id')} | Status: {detection.get('status')} | Ticket: {detection.get('pwd_ticket_id')}")
            else:
                print(f"[{i+1}/{count}] HTTP {resp.status_code}: {resp.text}")
        except Exception as e:
            print(f"[{i+1}/{count}] Connection Error to Orchestrator: {e}")

        time.sleep(interval_sec)

    print("\nTelemetry batch complete. Check Computer A Command Dashboard.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UrbanSight AI Edge Telemetry Node")
    parser.add_argument("--host", default="http://192.168.1.5:8000", help="URL of Computer A Master Orchestrator")
    parser.add_argument("--bus", default="BMTC-KA01-E542", help="Bus ID identifier")
    parser.add_argument("--interval", type=float, default=1.5, help="Seconds between detections")
    parser.add_argument("--count", type=int, default=10, help="Number of telemetry cycles to run")
    args = parser.parse_args()

    stream_edge_telemetry(args.host, args.bus, args.interval, args.count)
