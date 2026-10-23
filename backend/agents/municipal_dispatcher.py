"""
UrbanSight AI — Agent 3: Autonomous Municipal Dispatcher
Auto-files PWD work-orders with CPWD Schedule of Rates (SOR) mapping, SLA allocation, and jurisdiction routing.
"""

import random
from typing import Dict, Any, Optional, Tuple, List, Union
from datetime import datetime
from backend.models import (
    HazardDetection, PWDWorkOrder, HazardType, SeverityLevel, TicketStatus
)

# CPWD Schedule of Rates (SOR 2023-2026) Specifications
CPWD_SOR_REGISTRY = {
    HazardType.POTHOLE: {
        "sor_code": "CPWD-16.14.2",
        "description": "Repair of potholes in bituminous surface with Dense Bituminous Macadam (DBM)",
        "methodology": "Mill defective bituminous patch to 50mm, apply RS-1 bitumen emulsion tack coat @ 0.25 kg/sqm, lay hot DBM mix, and compact with vibratory roller.",
        "base_cost_inr": 4200.0
    },
    HazardType.ROAD_CRACK: {
        "sor_code": "CPWD-16.12.1",
        "description": "Sealing of longitudinal, transverse, and alligator cracks in asphalt pavement",
        "methodology": "Clear crack groove using high-pressure compressed air lance, inject polymer-modified hot elastomeric sealant, and dust with fine stone powder.",
        "base_cost_inr": 1850.0
    },
    HazardType.WATERLOGGING: {
        "sor_code": "CPWD-16.15.1",
        "description": "Stormwater drainage desilting and carriageway camber slope correction",
        "methodology": "Excavate silt and plastic obstruction from roadside RCC catch pits, flush conduit drains, and regrade bituminous shoulders to 2.5% camber.",
        "base_cost_inr": 6500.0
    },
    HazardType.CONGESTION: {
        "sor_code": "CPWD-16.08.3",
        "description": "Bottleneck mitigation and high-visibility thermoplastic lane demarcation",
        "methodology": "Apply 2.5mm retro-reflective thermoplastic pavement markings and notify Traffic Police Control for arterial signal phase retiming.",
        "base_cost_inr": 1200.0
    },
    HazardType.ROAD_DEBRIS: {
        "sor_code": "CPWD-16.03.4",
        "description": "Carriageway hazard obstacle clearance and mechanical vacuum sweeping",
        "methodology": "Deploy rapid-response municipal debris truck, clear heavy rubble/fallen branches from active lane, and sweep fine aggregate.",
        "base_cost_inr": 1500.0
    },
    HazardType.ACCIDENT: {
        "sor_code": "CPWD-16.01.0",
        "description": "Emergency carriageway clearance, barrier repair, and incident perimeter securing",
        "methodology": "Coordinate emergency towing, erect retro-reflective safety barricades, clear vehicular fluid spills with absorbent sand, and repair crash barriers.",
        "base_cost_inr": 9800.0
    }
}


class MunicipalDispatcherAgent:
    """
    Agent 3: Autonomous Municipal Dispatcher.
    - Evaluates consensus threshold: pass_count >= 2 OR severity == CRITICAL_P1.
    - Resolves geographic jurisdiction (BBMP wards, MCC Mysuru).
    - Maps defect to official Central Public Works Department (CPWD) Schedule of Rates (SOR).
    - Enforces municipal repair SLA: <24h (P1), <48h (P2), <72h (P3).
    - Auto-generates structured PWD Work Orders.
    - Produces itemized CPWD tender vouchers and cost estimates.
    """

    def __init__(self):
        self.agent_name = "Agent 3: Municipal Dispatch"
        self.ticket_sequence = 1000

    def resolve_jurisdiction(self, location_name: str, lat: float, lng: float) -> str:
        """
        Resolves municipal zone and ward jurisdiction based on location name and coordinates.
        Covers Bengaluru (BBMP) and Mysuru (MCC) arterial corridors.
        """
        loc_lower = location_name.lower()

        # Mysuru corridor
        if "mysuru" in loc_lower or "vvce" in loc_lower or (12.25 <= lat <= 12.38 and 76.55 <= lng <= 76.75):
            return "MCC Mysuru Engineering Ward 9 / PWD Mysuru Division"

        # Bengaluru zones
        if any(k in loc_lower for k in ["bellandur", "outer ring road", "orr", "sarjapur", "marathahalli", "whitefield", "ecoworld"]):
            return "BBMP Mahadevapura Ward 85 / PWD Division 3"
        elif any(k in loc_lower for k in ["silk board", "koramangala", "btm", "electronic city", "hsr"]):
            return "BBMP South Division Ward 142 / PWD Division 4"
        elif any(k in loc_lower for k in ["banashankari", "kengeri", "rr nagar", "rajarajeshwari"]):
            return "BBMP RR Nagar Division Ward 160 / PWD Banashankari"
        elif any(k in loc_lower for k in ["majestic", "kasturba", "cbd", "mg road", "vidhana"]):
            return "BBMP Central Ward Dispatch / PWD Zone 1"
        elif any(k in loc_lower for k in ["hebbal", "yelahanka", "manyata"]):
            return "BBMP East Division / Yelahanka Zone 2"

        # Default fallback
        if 12.8 <= lat <= 13.1 and 77.4 <= lng <= 77.8:
            return "BBMP Central Engineering Ward Dispatch / PWD Zone 1"
        elif 12.2 <= lat <= 12.4 and 76.5 <= lng <= 76.8:
            return "MCC Mysuru Engineering Ward / PWD Division"
        return "BBMP Ward 142 / PWD Division 4"

    def compute_sla_hours(self, severity: SeverityLevel) -> int:
        """
        Enforces municipal SLA based on defect severity:
        - CRITICAL_P1: <24 hours
        - HIGH_P2: <48 hours
        - MEDIUM_P3: <72 hours
        - LOW_P4: <120 hours
        """
        if severity == SeverityLevel.CRITICAL_P1:
            return 24
        elif severity == SeverityLevel.HIGH_P2:
            return 48
        elif severity == SeverityLevel.MEDIUM_P3:
            return 72
        else:
            return 120

    def should_dispatch(self, hazard: HazardDetection) -> bool:
        """
        Determines if a hazard qualifies for autonomous PWD work-order generation:
        - Already dispatched: False
        - pass_count >= 2 (verified multi-pass consensus)
        - OR severity == CRITICAL_P1 (immediate fast-track emergency)
        """
        if hazard.status == TicketStatus.AUTO_DISPATCHED or hazard.pwd_ticket_id is not None:
            return False

        if hazard.severity == SeverityLevel.CRITICAL_P1 or hazard.pass_count >= 2:
            return True

        return False

    def generate_work_order(self, hazard: HazardDetection) -> PWDWorkOrder:
        """
        Generates a legally formatted municipal PWD work order bound to CPWD SOR code.
        """
        self.ticket_sequence += 1
        ticket_id = f"PWD-2026-OCT-{random.randint(1000, 9999):04d}"

        jurisdiction = self.resolve_jurisdiction(
            location_name=hazard.location_name,
            lat=hazard.lat,
            lng=hazard.lng
        )

        sla_hours = self.compute_sla_hours(hazard.severity)
        sor_info = CPWD_SOR_REGISTRY.get(hazard.hazard_type, {
            "sor_code": "CPWD-16.14.2",
            "description": "Standard carriageway bituminous maintenance.",
            "methodology": "Standard carriageway bituminous maintenance.",
            "base_cost_inr": 3500.0
        })

        work_order = PWDWorkOrder(
            ticket_id=ticket_id,
            hazard_id=hazard.id,
            hazard_type=hazard.hazard_type,
            severity=hazard.severity,
            location_name=hazard.location_name,
            lat=hazard.lat,
            lng=hazard.lng,
            cluster_count=hazard.pass_count,
            sla_hours=sla_hours,
            dispatched_to=jurisdiction,
            status=TicketStatus.AUTO_DISPATCHED,
            cpwd_sor_code=sor_info["sor_code"],
            repair_methodology=sor_info["methodology"],
            estimated_cost_inr=sor_info["base_cost_inr"]
        )

        return work_order

    def evaluate_and_dispatch(
        self,
        hazard: HazardDetection,
        work_orders_list: List[PWDWorkOrder]
    ) -> Tuple[Optional[PWDWorkOrder], bool, str]:
        """
        Evaluates a canonical hazard and auto-dispatches to PWD if consensus threshold is met.
        Mutates hazard status and prepends work order.

        Returns: (work_order_or_none, dispatched_flag, log_message)
        """
        if not self.should_dispatch(hazard):
            return None, False, f"Hazard {hazard.id} pending further multi-pass consensus (passes: {hazard.pass_count}, sev: {hazard.severity.value})"

        work_order = self.generate_work_order(hazard)

        # Mutate hazard state
        hazard.status = TicketStatus.AUTO_DISPATCHED
        hazard.pwd_ticket_id = work_order.ticket_id

        # Prepend to master work order registry
        work_orders_list.insert(0, work_order)

        msg = (
            f"Auto-filed PWD Work Order #{work_order.ticket_id} for {hazard.location_name} "
            f"[{work_order.cpwd_sor_code} · SLA <{work_order.sla_hours}h] -> Dispatched to: {work_order.dispatched_to}"
        )
        return work_order, True, msg

    def generate_voucher_data(
        self,
        target: Optional[Union[PWDWorkOrder, str]] = None,
        work_order: Optional[PWDWorkOrder] = None,
        hazard: Optional[HazardDetection] = None,
        ticket_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        if isinstance(target, PWDWorkOrder):
            wo = target
            ticket_id = wo.ticket_id
        elif isinstance(work_order, PWDWorkOrder):
            wo = work_order
            ticket_id = ticket_id or (str(target) if target else wo.ticket_id)
        else:
            wo = None
            ticket_id = ticket_id or (str(target) if target else "PWD-OCT-0941")
        """
        Generates itemized CPWD Schedule of Rates (SOR 2024) tender voucher and cost breakdown.
        Polymorphic: Accepts either PWDWorkOrder directly or ticket_id with optional work_order.
        """


        sor_code = wo.cpwd_sor_code if wo and wo.cpwd_sor_code else "CPWD-16.14.2"
        base_cost = wo.estimated_cost_inr if wo and wo.estimated_cost_inr else 4200.0
        severity = wo.severity if wo else SeverityLevel.CRITICAL_P1
        hazard_type = wo.hazard_type if wo else HazardType.POTHOLE
        location_name = wo.location_name if wo else "Bengaluru Transit Corridor"
        dispatched_to = wo.dispatched_to if wo else "BBMP Mahadevapura Ward 85 / PWD Division 3"
        sla_hours = wo.sla_hours if wo else 24
        status = wo.status.value if wo and hasattr(wo.status, "value") else (str(wo.status) if wo else "AUTO_DISPATCHED")
        created_at = wo.created_at if wo else datetime.now().isoformat()
        cluster_count = wo.cluster_count if wo else 1
        hazard_id = wo.hazard_id if wo else f"HAZ-{ticket_id}"

        # Taxes and subtotals
        gst_rate = 18.0
        gst_amount = round(base_cost * 0.18, 2)
        total_sanction_inr = round(base_cost + gst_amount, 2)

        # Line items and BOQ items
        material_cost = round(base_cost * 0.55, 2)
        labor_cost = round(base_cost * 0.28, 2)
        machinery_cost = round(base_cost * 0.17, 2)

        boq_items = [
            {
                "item_code": "16.2.1",
                "description": "Surface cleaning, pneumatic dust blast & tack coat with bitumen emulsion @ 0.25 kg/sqm",
                "quantity": 2.40,
                "unit": "sqm",
                "rate_inr": 45.0,
                "amount_inr": 108.0
            },
            {
                "item_code": "16.2.2",
                "description": f"Supplying and laying cold-mix bituminous mastic patch per {sor_code}",
                "quantity": round(base_cost / 10000.0, 3) if base_cost > 0 else 0.24,
                "unit": "cum",
                "rate_inr": 6800.0,
                "amount_inr": round(base_cost - 558.0, 2) if base_cost > 558 else base_cost
            },
            {
                "item_code": "LAB-04",
                "description": "Skilled pavement compactor labor and retro-reflective traffic barricades deployment",
                "quantity": 1.0,
                "unit": "shift",
                "rate_inr": 450.0,
                "amount_inr": 450.0
            }
        ]

        line_items = [
            {
                "item_no": "1.1",
                "description": "Bituminous mix (DBM/Bitumen Emulsion RS-1) conforming to MORTH Sec 3000",
                "category": "Material",
                "unit": "sq.m / cu.m",
                "amount_inr": material_cost
            },
            {
                "item_no": "1.2",
                "description": "Skilled & Semi-skilled asphalt mason, road gang, and traffic flagger charges",
                "category": "Labor",
                "unit": "Mandays",
                "amount_inr": labor_cost
            },
            {
                "item_no": "1.3",
                "description": "Tandem vibratory roller (8-10 tonne), air compressor lance, asphalt cutter fuel & hire",
                "category": "Plant & Machinery",
                "unit": "Machine Hours",
                "amount_inr": machinery_cost
            }
        ]

        clean_ticket = ticket_id.replace("PWD-", "")
        checksum = f"CPWD-{clean_ticket}-INR-{int(total_sanction_inr)}"

        sor_details = CPWD_SOR_REGISTRY.get(hazard_type, {
            "description": "Bituminous carriageway repair under CPWD Works Manual",
            "methodology": "Mill defective patch, apply tack coat, lay hot mix DBM, compact with vibratory roller."
        })

        penalty_clause = (
            f"Mandatory SLA compliance: <{sla_hours} hours. "
            "Liquidated damages penalty of 1.0% per 12 hours delay beyond SLA, "
            "capped at 10% contract value, as per CPWD Works Manual Section 29.3 & BBMP Standard Tender Conditions."
        )

        return {
            "voucher_id": f"VOUCHER-{clean_ticket}",
            "ticket_id": ticket_id,
            "hazard_id": hazard_id,
            "sanction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
            "issuing_authority": "Office of Executive Engineer, Road Infrastructure Division, Urban Development Dept.",
            "jurisdiction": dispatched_to,
            "ward": dispatched_to,
            "location": location_name,
            "location_name": location_name,
            "lat": wo.lat if wo else 12.9250,
            "lng": wo.lng if wo else 77.6760,
            "cluster_count": cluster_count,
            "hazard_type": hazard_type.value if hasattr(hazard_type, "value") else str(hazard_type),
            "severity": severity.value if hasattr(severity, "value") else str(severity),
            "status": status,
            "cpwd_sor_code": sor_code,
            "sor_description": sor_details.get("description", "Standard Bituminous Repair"),
            "repair_methodology": sor_details.get("methodology", ""),
            "boq_items": boq_items,
            "line_items": line_items,
            "subtotal_inr": base_cost,
            "gst_rate_percent": gst_rate,
            "gst_rate_pct": gst_rate,
            "gst_amount_inr": gst_amount,
            "total_sanction_inr": total_sanction_inr,
            "total_estimated_inr": total_sanction_inr,
            "sla_hours": sla_hours,
            "penalty_clause": penalty_clause,
            "compliance_standards": ["CPWD SOR 2024", "IRC:SP:72-2015", "MORTH Sec 3000", "DPDP Act 2023 §2(t)"],
            "verification_checksum": checksum,
            "created_at": created_at
        }
