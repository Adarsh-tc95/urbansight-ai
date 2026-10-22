"""
UrbanSight AI — Computer A Master Remote Controller
Allows the Orchestrator on Computer A to check node health on Computer B,
trigger remote edge model benchmarks, and verify distributed telemetry over LAN.
"""

import requests
import json
import time

COMPUTER_B_URL = "http://192.168.1.6:8080"
LOCAL_ORCHESTRATOR_URL = "http://127.0.0.1:8000"

def ping_node_b():
    print(f"[Remote Controller] Pinging Edge Worker Node B at {COMPUTER_B_URL}...")
    try:
        r = requests.get(f"{COMPUTER_B_URL}/api/health", timeout=3.0)
        if r.status_code == 200:
            print(f"[Remote Controller] SUCCESS: Node B is ONLINE! Details: {json.dumps(r.json())}")
            return True
        else:
            print(f"[Remote Controller] Node B responded with HTTP {r.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[Remote Controller] Node B not yet responding on port 8080 ({e}).")
        print(f"Make sure 'python distributed/bridge_server.py' is running on Computer B (192.168.1.6).")
        return False

def trigger_remote_benchmark(model_name="YOLOv10s-ORDDC24", iterations=100):
    print(f"\n[Remote Controller] Requesting edge model benchmark for '{model_name}' on Node B...")
    try:
        r = requests.post(
            f"{COMPUTER_B_URL}/api/benchmark-model",
            json={"model_name": model_name, "iterations": iterations},
            timeout=10.0
        )
        if r.status_code == 200:
            res = r.json()
            print(f"[Remote Controller] Benchmark Results from Node B:")
            print(f"  • Model: {res['model']}")
            print(f"  • Average Latency: {res['avg_latency_ms']} ms")
            print(f"  • Estimated FPS: {res['estimated_fps']} FPS")
            print(f"  • Compute Target: {res['target_hardware']}")
            return res
    except Exception as e:
        print(f"[Remote Controller] Error triggering remote benchmark: {e}")
    return None

if __name__ == "__main__":
    ping_node_b()
