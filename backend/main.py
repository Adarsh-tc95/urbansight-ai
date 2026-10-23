import os
import random
import io
import csv
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from backend.models import (
    BusTelemetry, HazardDetection, PWDWorkOrder, DriverAdvisory,
    AgentEventLog, HazardType, SeverityLevel, TicketStatus
)
from backend.agents.orchestrator import UrbanSightOrchestrator

app = FastAPI(
    title="UrbanSight AI — Mobile Urban Intelligence Platform",
    description="Multi-Agent AI framework for continuous transit-fleet road sensing, DBSCAN spatial clustering, automated PWD dispatch, and driver advisories (SIH26124).",
    version="2.0.0"
)

# CORS Middleware for local and cross-origin dashboard access
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

class TicketStatusUpdateRequest(BaseModel):
    status: TicketStatus
    remarks: Optional[str] = "Field update by Quick Response Crew"
    crew_id: Optional[str] = "VAN-04"

# -------------------------------------------------------------
# Frontend View Routes
# -------------------------------------------------------------

@app.get("/")
def read_root(request: Request):
    """Renders the main UrbanSight AI Command Dashboard."""
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/driver")
@app.get("/console")
def read_driver_console(request: Request):
    """Renders the dedicated In-Cab Driver HUD Console UI."""
    return templates.TemplateResponse(request=request, name="driver_console.html")

@app.get("/citizen")
@app.get("/portal")
def read_citizen_portal(request: Request):
    """Renders the public citizen repair tracking portal."""
    return templates.TemplateResponse(request=request, name="citizen_portal.html")

@app.get("/field-crew")
@app.get("/crew")
def read_field_crew(request: Request):
    """Renders the mobile PWD field technician PWA."""
    return templates.TemplateResponse(request=request, name="field_crew.html")

@app.get("/voucher")
def read_voucher(request: Request):
    """Renders the official printable CPWD tender voucher."""
    return templates.TemplateResponse(request=request, name="voucher.html")

# -------------------------------------------------------------
# Core API Endpoints
# -------------------------------------------------------------

@app.get("/api/health")
def health_check():
    """Health check endpoint for local and distributed monitoring."""
    return {
        "status": "HEALTHY",
        "service": "UrbanSight AI Command Orchestrator",
        "version": "2.0.0",
        "active_agents": 4,
        "agents": [
            "VisionPerceptionAgent (YOLOv8/DPDP Blur)",
            "GeospatialClusteringAgent (DBSCAN/IMU Fusion)",
            "MunicipalDispatcherAgent (CPWD SOR/Auto-Dispatch)",
            "FleetAdvisoryAgent (Driver WebSocket Alerts)"
        ],
        "buses_online": len(orchestrator.buses),
        "hazards_tracked": len(orchestrator.hazards),
        "work_orders_filed": len(orchestrator.work_orders)
    }

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

@app.get("/api/work-orders/{ticket_id}/voucher")
def get_work_order_voucher(ticket_id: str):
    """Returns itemized CPWD Schedule of Rates tender voucher breakdown for a work order."""
    clean_id = ticket_id.strip()
    wo = next((w for w in orchestrator.work_orders if w.ticket_id == clean_id or clean_id in w.ticket_id), None)
    if not wo:
        raise HTTPException(status_code=404, detail=f"Work order {ticket_id} not found")
    hazard = next((h for h in orchestrator.hazards if h.id == wo.hazard_id or h.pwd_ticket_id == wo.ticket_id), None)
    return orchestrator.dispatcher_agent.generate_voucher_data(wo, hazard)

@app.post("/api/work-orders/{ticket_id}/status")
@app.post("/api/work-orders/{ticket_id}/resolve")
def update_work_order_status(ticket_id: str, req: TicketStatusUpdateRequest):
    """Updates work order lifecycle status (e.g. IN_PROGRESS, RESOLVED) and logs agent event."""
    clean_id = ticket_id.strip()
    wo = next((w for w in orchestrator.work_orders if w.ticket_id == clean_id or clean_id in w.ticket_id), None)
    if not wo:
        raise HTTPException(status_code=404, detail=f"Work order {ticket_id} not found")

    wo.status = req.status
    hazard = next((h for h in orchestrator.hazards if h.id == wo.hazard_id or h.pwd_ticket_id == wo.ticket_id), None)
    if hazard:
        hazard.status = req.status

    orchestrator.event_logs.insert(0, AgentEventLog(
        id=f"EVT-{len(orchestrator.event_logs)+1:04d}",
        agent_name="Agent 3: PWD Dispatch",
        action="TICKET_STATUS_UPDATED",
        detail=f"Ticket #{wo.ticket_id} moved to {req.status.value} by {req.crew_id}. Remarks: {req.remarks}"
    ))

    return {
        "status": "SUCCESS",
        "ticket_id": wo.ticket_id,
        "new_status": wo.status,
        "crew_id": req.crew_id,
        "remarks": req.remarks
    }

@app.get("/api/advisories")
def get_advisories():
    return orchestrator.advisories

@app.get("/api/events")
def get_event_logs():
    return orchestrator.event_logs

@app.get("/api/agents/status")
def get_agents_status():
    """Returns detailed status and stats for each of the 4 autonomous agents."""
    return {
        "agent_1_vision": {
            "name": "Vision Perception Agent",
            "model": "YOLOv8-Nano (TensorRT FP16 / 30 FPS)",
            "privacy_guard": "DPDP Act 2023 §2(t) Zero-Persistence YuNet Gaussian Masking",
            "confidence_threshold": 0.70,
            "status": "ACTIVE"
        },
        "agent_2_clustering": {
            "name": "Geospatial Clustering Agent",
            "algorithm": "DBSCAN (epsilon=25m, Haversine metric)",
            "sensor_fusion": "6-Axis IMU Acceleration Shock (-az < -0.25g / bump rejection)",
            "status": "ACTIVE"
        },
        "agent_3_dispatcher": {
            "name": "Municipal Dispatcher Agent",
            "jurisdictions": ["BBMP Mahadevapura Ward 85", "BBMP East", "MCC Mysuru Ward 9"],
            "rate_schedule": "CPWD Schedule of Rates 2023/2024",
            "sla_rules": {"CRITICAL_P1": "<24h", "HIGH_P2": "<48h", "MEDIUM_P3": "<72h"},
            "status": "ACTIVE"
        },
        "agent_4_advisory": {
            "name": "Fleet Advisory Agent",
            "broadcast_radius_m": 300,
            "protocol": "WebSocket / MQTT Telemetry",
            "advisory_types": ["SPEED_REDUCTION", "LANE_MERGE", "CAUTION"],
            "status": "ACTIVE"
        }
    }

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

@app.get("/api/export-csv")
def export_csv():
    """Exports all municipal work orders in standard CSV format for ULB / PWD integration."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Ticket ID", "Hazard ID", "Hazard Type", "Severity", "Location",
        "Latitude", "Longitude", "Cluster Passes", "SLA Hours", "Jurisdiction Ward",
        "Status", "CPWD SOR Code", "Estimated Cost INR", "Created At"
    ])
    for w in orchestrator.work_orders:
        writer.writerow([
            w.ticket_id, w.hazard_id,
            w.hazard_type.value if hasattr(w.hazard_type, 'value') else w.hazard_type,
            w.severity.value if hasattr(w.severity, 'value') else w.severity,
            w.location_name, w.lat, w.lng, w.cluster_count, w.sla_hours,
            w.dispatched_to,
            w.status.value if hasattr(w.status, 'value') else w.status,
            w.cpwd_sor_code or "",
            w.estimated_cost_inr or "",
            w.created_at
        ])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=urbansight_pwd_work_orders.csv"}
    )

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
