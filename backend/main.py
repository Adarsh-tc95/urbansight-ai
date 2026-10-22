import os
import random
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from backend.models import (
    BusTelemetry, HazardDetection, PWDWorkOrder, DriverAdvisory,
    AgentEventLog, HazardType, SeverityLevel
)
from backend.agents.orchestrator import UrbanSightOrchestrator

app = FastAPI(
    title="UrbanSight AI — Mobile Urban Intelligence Platform",
    description="Multi-Agent AI framework for continuous transit-fleet road sensing, DBSCAN spatial clustering, automated PWD dispatch, and driver advisories (SIH26124).",
    version="2.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Initialize Orchestrator Singleton
orchestrator = UrbanSightOrchestrator()

class DetectSimulationRequest(BaseModel):
    bus_id: Optional[str] = "BMTC-KA01-E542"
    hazard_type: Optional[HazardType] = HazardType.POTHOLE
    lat: Optional[float] = 12.9350
    lng: Optional[float] = 77.6820
    location_name: Optional[str] = "Sarjapur-ORR Junction (Near EcoWorld)"
    confidence: Optional[float] = 0.965
    damage_depth_cm: Optional[float] = 9.8
    affected_length_m: Optional[float] = None
    estimated_area_sqm: Optional[float] = None
    z_shock: Optional[float] = None

@app.get("/")
def read_root(request: Request):
    """Renders the main UrbanSight AI Command Dashboard."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/metrics")
def get_metrics():
    return orchestrator.get_system_metrics()

@app.get("/api/buses")
def get_buses():
    return orchestrator.buses

@app.get("/api/hazards")
def get_hazards():
    return orchestrator.hazards

@app.get("/api/work-orders")
def get_work_orders():
    return orchestrator.work_orders

@app.get("/api/advisories")
def get_advisories():
    return orchestrator.advisories

@app.get("/api/events")
def get_event_logs():
    return orchestrator.event_logs

@app.post("/api/simulate-detection")
def simulate_detection(req: DetectSimulationRequest):
    try:
        detection = orchestrator.process_edge_detection(
            bus_id=req.bus_id,
            hazard_type=req.hazard_type,
            lat=req.lat,
            lng=req.lng,
            location_name=req.location_name,
            confidence=req.confidence if req.confidence is not None else 0.95,
            damage_depth_cm=req.damage_depth_cm,
            affected_length_m=req.affected_length_m,
            estimated_area_sqm=req.estimated_area_sqm,
            z_shock=req.z_shock
        )
        return {
            "status": "SUCCESS",
            "detection": detection,
            "metrics": orchestrator.get_system_metrics()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/export-geojson")
def export_geojson():
    """Exports all canonical road hazards in standard OGC GeoJSON FeatureCollection format for Smart Cities ICCC integration."""
    features = []
    for h in orchestrator.hazards:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [h.lng, h.lat]
            },
            "properties": {
                "id": h.id,
                "hazard_type": h.hazard_type,
                "severity": h.severity,
                "confidence": h.confidence,
                "location_name": h.location_name,
                "damage_depth_cm": h.damage_depth_cm,
                "pass_count": h.pass_count,
                "cluster_id": h.cluster_id,
                "status": h.status,
                "pwd_ticket_id": h.pwd_ticket_id,
                "timestamp": h.timestamp
            }
        })
    return {
        "type": "FeatureCollection",
        "metadata": {
            "generated_by": "UrbanSight AI Multi-Agent Intelligence Grid",
            "crs": "urn:ogc:def:crs:OGC:1.3:CRS84",
            "total_features": len(features)
        },
        "features": features
    }

@app.get("/api/buses/{bus_id}/telemetry")
def get_bus_telemetry(bus_id: str):
    """Retrieves live telemetry and active in-cab driver advisories for a specific transit bus."""
    bus = next((b for b in orchestrator.buses if b.bus_id == bus_id), None)
    if not bus:
        raise HTTPException(status_code=404, detail=f"Bus {bus_id} not found in fleet grid")
    bus_advisories = [a for a in orchestrator.advisories if a.bus_id == bus_id]
    return {
        "bus": bus,
        "active_advisories": bus_advisories,
        "camera_feed": {
            "status": bus.camera_status,
            "privacy_redaction": "ACTIVE_DPDP_COMPLIANT",
            "target_resolution": "1080p @ 30FPS"
        }
    }

@app.post("/api/reset")
def reset_system():
    global orchestrator
    orchestrator = UrbanSightOrchestrator()
    return {"status": "RESET_SUCCESSFUL"}
