"""
UrbanSight AI — Computer B Edge Bus Telemetry Generator
Simulates a moving transit bus fleet on Computer B streaming live hazard detections
and IMU vibration readings across the LAN to Computer A (Master Orchestrator).
Supports realistic GPS route trajectories from distributed/routes/*.json.
"""

import time
import json
import os
import random
import requests
import argparse
from typing import Dict, Any, List

# Built-in fallback route coordinates along Bengaluru & Mysuru corridors
DEFAULT_ROUTE_WAYPOINTS = [
    {"name": "Silk Board Junction Flyover Approach", "lat": 12.9172, "lng": 77.6228, "hazard": "POTHOLE", "depth": 9.4, "z_shock": -0.42},
    {"name": "Bellandur EcoSpace Main Arterial", "lat": 12.9260, "lng": 77.6765, "hazard": "ROAD_CRACK", "depth": 3.1, "z_shock": -0.15},
    {"name": "Marathahalli Underpass Lane 2", "lat": 12.9560, "lng": 77.7010, "hazard": "WATERLOGGING", "depth": None, "z_shock": None},
    {"name": "Tin Factory Junction Corridor", "lat": 12.9940, "lng": 77.6610, "hazard": "CONGESTION", "depth": None, "z_shock": None},
    {"name": "Kasturba Road Bottleneck", "lat": 12.9730, "lng": 77.5960, "hazard": "POTHOLE", "depth": 7.8, "z_shock": -0.38},
    {"name": "VVCE Ring Road Junction, Mysuru", "lat": 12.3190, "lng": 76.6450, "hazard": "POTHOLE", "depth": 8.6, "z_shock": -0.40},
    {"name": "Hunsur Road Speed Table (Speed Bump Check)", "lat": 12.3140, "lng": 76.6320, "hazard": "POTHOLE", "depth": 4.0, "z_shock": +0.55} # Will be rejected by IMU!
]

def load_route_waypoints(route_file: str) -> List[Dict[str, Any]]:
    """Loads waypoint sequence from a specified JSON route file."""
    if not os.path.exists(route_file):
        print(f"[WARN] Route file '{route_file}' not found. Using default corridor waypoints.")
        return DEFAULT_ROUTE_WAYPOINTS
    
    try:
        with open(route_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        waypoints = data.get("waypoints", [])
        print(f"[INFO] Loaded route: {data.get('route_name', route_file)} ({len(waypoints)} waypoints)")
        return waypoints
    except Exception as e:
        print(f"[ERROR] Failed to parse route file '{route_file}': {e}. Using defaults.")
        return DEFAULT_ROUTE_WAYPOINTS

def stream_edge_telemetry(orchestrator_url: str, bus_id: str, interval_sec: float = 1.5, count: int = 20, route_file: str = None):
    print(f"================================================================")
    print(f"UrbanSight AI — Computer B Edge Sensing Node Starting")
    print(f"Target Master Orchestrator: {orchestrator_url}")
    print(f"Simulating Bus: {bus_id}")
    if route_file:
        print(f"Route Trajectory File: {route_file}")
    print(f"================================================================\n")

    waypoints = load_route_waypoints(route_file) if route_file else DEFAULT_ROUTE_WAYPOINTS
    hazard_waypoints = [wp for wp in waypoints if wp.get("hazard")]
    if not hazard_waypoints:
        hazard_waypoints = waypoints

    for i in range(count):
        # Pick waypoint sequentially or with slight jitter
        wp = hazard_waypoints[i % len(hazard_waypoints)]
        
        # Add small jitter to simulate repeat passes for DBSCAN clustering
        jitter_lat = wp["lat"] + (random.random() - 0.5) * 0.0001
        jitter_lng = wp["lng"] + (random.random() - 0.5) * 0.0001

        payload = {
            "bus_id": bus_id,
            "hazard_type": wp.get("hazard", "POTHOLE"),
            "lat": round(jitter_lat, 6),
            "lng": round(jitter_lng, 6),
            "location_name": wp.get("name", "Corridor Arterial"),
            "confidence": round(random.uniform(0.91, 0.98), 3),
            "damage_depth_cm": wp.get("depth", 8.5),
            "z_shock": wp.get("z_shock")
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
                shock_str = f" | Shock: {wp.get('z_shock')}g" if wp.get('z_shock') is not None else ""
                print(f"[{i+1}/{count}] OK ({elapsed_ms:.1f}ms LAN): {payload['hazard_type']} @ {wp['name']}{shock_str} "
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
    parser.add_argument("--bus", default="BMTC-KA57-E912", help="Bus ID identifier")
    parser.add_argument("--interval", type=float, default=1.5, help="Seconds between detections")
    parser.add_argument("--count", type=int, default=10, help="Number of telemetry cycles to run")
    parser.add_argument("--route", default=None, help="Path to JSON route waypoints file (e.g., distributed/routes/bmtc_orr.json)")
    args = parser.parse_args()

    stream_edge_telemetry(args.host, args.bus, args.interval, args.count, args.route)
