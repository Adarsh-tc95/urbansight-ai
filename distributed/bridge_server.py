"""
UrbanSight AI — Computer B Edge Worker Bridge Server
Run this script on Computer B (192.168.1.6) to allow Computer A (Master Orchestrator)
to remotely invoke edge model benchmarks, trigger edge camera simulations, and access hardware telemetry.
"""

import sys
import subprocess
import platform
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

app = FastAPI(
    title="UrbanSight AI — Edge Worker Node (Computer B)",
    description="Remote bridge for distributed multi-agent transit sensing and GPU model execution.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExecCommandRequest(BaseModel):
    command: str
    timeout_sec: Optional[int] = 30

class ModelBenchmarkRequest(BaseModel):
    model_name: Optional[str] = "YOLOv10s-ORDDC24"
    batch_size: Optional[int] = 1
    iterations: Optional[int] = 50

@app.get("/")
def read_root():
    return {
        "node_id": "URBANSIGHT-EDGE-NODE-B",
        "role": "High-Throughput Edge Camera & Vibration Inference Worker",
        "platform": platform.platform(),
        "python_version": sys.version,
        "status": "ONLINE_STANDBY"
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "hostname": platform.node(),
        "os": platform.system(),
        "cpu_count": os.cpu_count()
    }

@app.post("/api/exec")
def execute_command(req: ExecCommandRequest):
    """Executes a command on Computer B and returns stdout/stderr."""
    try:
        proc = subprocess.run(
            req.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=req.timeout_sec
        )
        return {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": proc.returncode
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail=f"Command timed out after {req.timeout_sec}s")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/benchmark-model")
def benchmark_model(req: ModelBenchmarkRequest):
    """Simulates on-device GPU inference latency for the specified model."""
    import time
    start = time.perf_counter()
    # Simulated tensor warmup & execution loop
    time.sleep(0.05)
    elapsed_ms = (time.perf_counter() - start) * 1000 / req.iterations
    return {
        "model": req.model_name,
        "iterations": req.iterations,
        "avg_latency_ms": round(elapsed_ms, 2),
        "estimated_fps": round(1000.0 / max(elapsed_ms, 0.1), 1),
        "target_hardware": platform.processor() or "GPU/NPU Worker"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting UrbanSight Edge Worker Bridge on 0.0.0.0:{port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
