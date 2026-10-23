import os
import random
import io
import csv
from datetime import datetime
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
from backend.agents.pci_engine import PCIEngine

app = FastAPI(
    title="UrbanSight AI — Mobile Urban Intelligence Platform",
    description="Multi-Agent AI framework for continuous transit-fleet road sensing, DBSCAN spatial clustering, automated PWD dispatch, and driver advisories (SIH26124).",
    version="2.1.0"
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
pci_engine = PCIEngine()

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

class WorkOrderStatusUpdate(BaseModel):
    status: Optional[str] = "RESOLVED"
    remarks: Optional[str] = "Pothole patch completed with hot DBM and compacted with vibratory roller."
    crew_id: Optional[str] = "BBMP-CREW-VAN-04"

# Alias for compatibility with Node B
TicketStatusUpdateRequest = WorkOrderStatusUpdate

# =============================================================================
# Frontend View Routes
# =============================================================================

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

# =============================================================================
# Core API & Telemetry Endpoints
# =============================================================================

@app.get("/api/health")
def health_check():
    """Health check endpoint for local and distributed monitoring."""
    return {
        "status": "HEALTHY",
        "service": "UrbanSight AI Command Orchestrator",
        "version": "2.1.0",
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

# =============================================================================
# Municipal Dispatch & CPWD Voucher APIs
# =============================================================================

def _find_work_order(ticket_id: str) -> Optional[PWDWorkOrder]:
    tid_clean = ticket_id.strip()
    tid_norm = tid_clean.replace("-2026", "")
    for w in orchestrator.work_orders:
        w_norm = w.ticket_id.replace("-2026", "")
        if w.ticket_id == tid_clean or w_norm == tid_norm or tid_clean in w.ticket_id:
            return w
    return None

@app.get("/api/work-orders/{ticket_id}/voucher")
def get_work_order_voucher(ticket_id: str):
    """Retrieves itemized CPWD Schedule of Rates tender voucher for a specific PWD ticket."""
    wo = _find_work_order(ticket_id)
    voucher = orchestrator.dispatcher_agent.generate_voucher_data(ticket_id=ticket_id, work_order=wo)
    return voucher

@app.post("/api/work-orders/{ticket_id}/resolve")
@app.post("/api/work-orders/{ticket_id}/status")
def update_work_order_status(ticket_id: str, req: WorkOrderStatusUpdate):
    """Updates work order lifecycle status (e.g. IN_PROGRESS, RESOLVED) from field crew."""
    wo = _find_work_order(ticket_id)
    if not wo:
        raise HTTPException(status_code=404, detail=f"Work Order {ticket_id} not found")

    new_status = TicketStatus.RESOLVED if "RESOLV" in (req.status or "").upper() else TicketStatus.IN_PROGRESS
    wo.status = new_status
    wo.resolved_at = datetime.now().isoformat() if new_status == TicketStatus.RESOLVED else None
    wo.resolution_remarks = req.remarks
    wo.assigned_crew_id = req.crew_id

    # Sync corresponding canonical hazard
    matched_hazard = next((h for h in orchestrator.hazards if h.pwd_ticket_id == ticket_id or h.id == wo.hazard_id), None)
    if matched_hazard:
        matched_hazard.status = new_status

    orchestrator._log_event(
        "Agent 3: Municipal Dispatch",
        f"WORK_ORDER_{new_status.value}",
        f"Ticket #{ticket_id} updated to {new_status.value} by field crew [{req.crew_id}]: {req.remarks}"
    )

    return {
        "status": "SUCCESS",
        "ticket_id": ticket_id,
        "new_status": new_status.value,
        "resolved_at": wo.resolved_at,
        "crew_id": wo.assigned_crew_id,
        "remarks": req.remarks,
        "work_order": wo
    }

@app.get("/api/export-csv")
def export_csv():
    """Exports all municipal work orders in official CPWD tabular CSV format."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Ticket ID", "Hazard Type", "Severity", "Ward / Jurisdiction",
        "Location", "Latitude", "Longitude", "Passes", "Status",
        "SLA Hours", "Cost INR", "CPWD SOR Code", "Created At", "Resolved At", "Crew ID"
    ])
    for w in orchestrator.work_orders:
        writer.writerow([
            w.ticket_id,
            w.hazard_type.value if hasattr(w.hazard_type, 'value') else str(w.hazard_type),
            w.severity.value if hasattr(w.severity, 'value') else str(w.severity),
            w.dispatched_to,
            w.location_name,
            w.lat,
            w.lng,
            w.cluster_count,
            w.status.value if hasattr(w.status, 'value') else str(w.status),
            w.sla_hours,
            w.estimated_cost_inr or 0.0,
            w.cpwd_sor_code or "CPWD-16.14.2",
            w.created_at,
            w.resolved_at or "PENDING",
            w.assigned_crew_id or "UNASSIGNED"
        ])
    csv_bytes = output.getvalue().encode("utf-8")
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=urbansight_cpwd_work_orders.csv"}
    )

# =============================================================================
# Edge Detection Simulation & Telemetry
# =============================================================================

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

@app.get("/api/pci-heatmap")
def get_pci_heatmap(days: int = 0):
    """Returns geospatial corridor polylines with ASTM D6433 Pavement Condition Index and degradation forecast."""
    return pci_engine.get_corridor_forecasts(days=days)

@app.get("/api/pci-summary")
def get_pci_summary(days: int = 0):
    """Returns executive city-wide road network health KPIs and predictive maintenance ROI."""
    return pci_engine.get_network_governance_summary(days=days)

@app.post("/api/reset")
def reset_system():
    global orchestrator
    orchestrator = UrbanSightOrchestrator()
    return {"status": "RESET_SUCCESSFUL"}
