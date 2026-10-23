/**
 * UrbanSight AI — Smart City ICCC Command System (Infothon 7.0)
 * Real-time GIS map, Edge Dashcam HUD Simulator, Multi-Agent Engine, PWD Work Orders
 */

document.addEventListener('DOMContentLoaded', () => {
    initClock();
    initLeafletMap();
    initDashcamSimulator();
    initEventLogFeed();
    initActionListeners();
    startRealtimePolling();
});

// Global State
const state = {
    buses: [
        { id: "BMTC-KA01-E542", route: "Outer Ring Road Express", lat: 12.9238, lng: 77.6745, speed: 24, heading: 45, marker: null },
        { id: "BMTC-KA57-E912", route: "Route 500D (Hebbal ↔ E-City)", lat: 12.9112, lng: 77.6380, speed: 18, heading: 180, marker: null },
        { id: "KSRTC-KA09-E102", route: "Mysuru Ring Road (VVCE)", lat: 12.3160, lng: 76.6413, speed: 32, heading: 90, marker: null },
        { id: "BMTC-KA03-E304", route: "Majestic ↔ Whitefield ITPL", lat: 12.9716, lng: 77.5946, speed: 15, heading: 115, marker: null }
    ],
    hazards: [
        { id: "HAZ-001", type: "POTHOLE", sev: "CRITICAL_P1", lat: 12.9250, lng: 77.6760, name: "ORR Bellandur Flyover Pillar 34", depth: "9.4cm", conf: "96.4%", passes: 14, ticket: "PWD-OCT-0941" },
        { id: "HAZ-002", type: "WATERLOGGING", sev: "HIGH_P2", lat: 12.9125, lng: 77.6395, name: "Silk Board Underpass South Lane", length: "35m", conf: "92.1%", passes: 8, ticket: "PWD-OCT-0882" },
        { id: "HAZ-003", type: "POTHOLE", sev: "CRITICAL_P1", lat: 12.3190, lng: 76.6450, name: "VVCE Ring Road Junction, Mysuru", depth: "8.6cm", conf: "94.8%", passes: 6, ticket: "PWD-OCT-0715" },
        { id: "HAZ-004", type: "CONGESTION", sev: "MEDIUM_P3", lat: 12.9730, lng: 77.5960, name: "Kasturba Road Bottleneck (9 km/h)", conf: "88.5%", passes: 12, ticket: null }
    ],
    workOrders: [
        { ticket: "PWD-OCT-0941", type: "POTHOLE", sev: "CRITICAL_P1", loc: "ORR Bellandur Flyover Pillar 34", passes: 14, sla: "41h 20m remaining", status: "DISPATCHED" },
        { ticket: "PWD-OCT-0882", type: "WATERLOGGING", sev: "HIGH_P2", loc: "Silk Board Underpass South Lane", passes: 8, sla: "19h 45m remaining", status: "CREW_ASSIGNED" },
        { ticket: "PWD-OCT-0715", type: "POTHOLE", sev: "CRITICAL_P1", loc: "VVCE Ring Road Junction, Mysuru", passes: 6, sla: "44h 10m remaining", status: "IN_PROGRESS" }
    ],
    logs: [
        { time: "19:54:10", agent: "Agent 1: Vision", text: "YOLOv8-Nano running @ 30 FPS. DPDP Gaussian face & plate blur ACTIVE." },
        { time: "19:54:02", agent: "Agent 2: DBSCAN", text: "Clustered 14 bus passes into canonical hazard #HAZ-001 (5m epsilon match)." },
        { time: "19:53:50", agent: "Agent 3: PWD Dispatch", text: "Auto-filed PWD Work Order #PWD-OCT-0941 with GPS & photo evidence (<180s SLA)." },
        { time: "19:53:35", agent: "Agent 4: Fleet Advisory", text: "Pushed WebSocket warning alert to oncoming buses on Bellandur corridor." }
    ],
    settings: {
        privacyBlur: true,
        nightMode: false,
        soundAlerts: false
    },
    map: null,
    pciLayerGroup: null
};

// 1. Clock Telemetry
function initClock() {
    const clockEl = document.getElementById('telemetry-clock');
    if (!clockEl) return;
    setInterval(() => {
        const now = new Date();
        clockEl.textContent = now.toTimeString().split(' ')[0] + " IST";
    }, 1000);
}

// 2. Leaflet GIS Map Initialization
function initLeafletMap() {
    const mapContainer = document.getElementById('gis-map');
    if (!mapContainer) return;

    // Centered over Bengaluru / Karnataka transit network
    state.map = L.map('gis-map', {
        zoomControl: true,
        scrollWheelZoom: true
    }).setView([12.9350, 77.6400], 12);

    // CartoDB Dark Matter Tiles
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        maxZoom: 19
    }).addTo(state.map);

    // Plot Initial Hazards
    renderHazardsOnMap();

    // Plot Initial Buses
    renderBusesOnMap();

    // Plot ASTM D6433 Pavement Condition Heatmap
    renderPCIHeatmap(0);
}

function renderHazardsOnMap() {
    state.hazards.forEach(h => {
        let color = '#FF5E1E';
        let iconClass = 'fa-triangle-exclamation';

        if (h.type === 'POTHOLE') {
            color = h.sev === 'CRITICAL_P1' ? '#EF4444' : '#FF5E1E';
            iconClass = 'fa-road';
        } else if (h.type === 'WATERLOGGING') {
            color = '#3B82F6';
            iconClass = 'fa-water';
        } else if (h.type === 'CONGESTION') {
            color = '#8B5CF6';
            iconClass = 'fa-car';
        }

        const markerHtml = `
            <div style="position:relative; width:30px; height:30px; display:flex; align-items:center; justify-content:center;">
                <div style="position:absolute; width:100%; height:100%; border-radius:50%; background:${color}; opacity:0.3; animation:pulse 1.8s infinite;"></div>
                <div style="width:20px; height:20px; border-radius:50%; background:${color}; color:#fff; display:flex; align-items:center; justify-content:center; font-size:10px; font-weight:800; box-shadow:0 0 10px ${color};">
                    <i class="fa-solid ${iconClass}"></i>
                </div>
            </div>
        `;

        const hazardIcon = L.divIcon({
            className: 'hazard-custom-marker',
            html: markerHtml,
            iconSize: [30, 30]
        });

        const popupContent = `
            <div style="color:#0F172A; font-family:'Plus Jakarta Sans',sans-serif; min-width:180px;">
                <div style="font-weight:800; font-size:12px; color:${color}; margin-bottom:4px;">
                    [${h.sev}] ${h.type}
                </div>
                <div style="font-size:11px; margin-bottom:6px;"><b>${h.name}</b></div>
                <div style="font-size:10px; color:#475569; margin-bottom:2px;">AI Confidence: <b>${h.conf}</b></div>
                ${h.depth ? `<div style="font-size:10px; color:#475569;">Measured Depth: <b>${h.depth}</b></div>` : ''}
                ${h.length ? `<div style="font-size:10px; color:#475569;">Submerged Length: <b>${h.length}</b></div>` : ''}
                <div style="font-size:10px; color:#475569; margin-top:4px;">DBSCAN Cluster Passes: <b>${h.passes} verified</b></div>
                ${h.ticket ? `<div style="margin-top:6px; background:#DCFCE7; color:#15803D; font-size:10px; font-weight:700; padding:2px 6px; border-radius:4px;">Auto Work-Order: ${h.ticket}</div>` : ''}
            </div>
        `;

        L.marker([h.lat, h.lng], { icon: hazardIcon })
            .bindPopup(popupContent)
            .addTo(state.map);
    });
}

function renderBusesOnMap() {
    state.buses.forEach(b => {
        const busHtml = `
            <div style="background:#00E5FF; color:#090D16; border-radius:50%; width:28px; height:28px; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:800; box-shadow:0 0 12px #00E5FF;">
                <i class="fa-solid fa-bus"></i>
            </div>
        `;

        const busIcon = L.divIcon({
            className: 'bus-custom-marker',
            html: busHtml,
            iconSize: [28, 28]
        });

        b.marker = L.marker([b.lat, b.lng], { icon: busIcon })
            .bindPopup(`
                <div style="color:#0F172A; font-family:'Plus Jakarta Sans',sans-serif;">
                    <div style="font-weight:800; font-size:12px; color:#0891B2;">${b.id}</div>
                    <div style="font-size:11px; margin:2px 0 6px;">${b.route}</div>
                    <div style="font-size:10px; color:#10B981;">● Camera: ONLINE (30 FPS)</div>
                    <div style="font-size:10px; color:#475569;">Speed: ${b.speed} km/h • Heading: ${b.heading}°</div>
                    <div style="font-size:10px; color:#475569;">Privacy Blur: <b>ACTIVE (DPDP)</b></div>
                </div>
            `)
            .addTo(state.map);
    });
}


// ASTM D6433 Standard Pavement Condition Index (PCI) Corridors Fallback Dataset
const FALLBACK_PCI_CORRIDORS = [
    {
        corridor_id: "CORR-01",
        name: "Outer Ring Road: Marathahalli ↔ Bellandur EcoSpace",
        jurisdiction: "BBMP Mahadevapura Ward 85",
        arterial_type: "High-Volume Transit Arterial (BMTC 500D)",
        coordinates: [
            [12.9560, 77.7010],
            [12.9480, 77.6965],
            [12.9410, 77.6900],
            [12.9350, 77.6820],
            [12.9260, 77.6765],
            [12.9240, 77.6730]
        ],
        base_pci: 58.0,
        decay_rate_k: 0.019,
        distress_items: ["3 Potholes (>8cm)", "2 Fatigue Cracks", "1 Flood Puddle"]
    },
    {
        corridor_id: "CORR-02",
        name: "Central Silk Board Junction ↔ HSR Layout Sector 1",
        jurisdiction: "BBMP South Ward 142",
        arterial_type: "Primary Metro & Freight Interchange",
        coordinates: [
            [12.9172, 77.6228],
            [12.9174, 77.6280],
            [12.9178, 77.6365],
            [12.9180, 77.6410]
        ],
        base_pci: 44.0,
        decay_rate_k: 0.024,
        distress_items: ["4 Deep Potholes (9.4cm)", "High Camber Waterlogging"]
    },
    {
        corridor_id: "CORR-03",
        name: "Electronic City Elevated Tollway Service Approach",
        jurisdiction: "BBMP Bommanahalli / ELCITA",
        arterial_type: "Expressway Feeder Corridor",
        coordinates: [
            [12.8960, 77.6445],
            [12.8840, 77.6565],
            [12.8705, 77.6685],
            [12.8600, 77.6750]
        ],
        base_pci: 74.0,
        decay_rate_k: 0.012,
        distress_items: ["1 Surface Crack", "1 Minor Dip"]
    },
    {
        corridor_id: "CORR-04",
        name: "Mysuru Ring Road: VVCE Gokulam ↔ Hunsur Road",
        jurisdiction: "MCC Mysuru Ward 9",
        arterial_type: "Urban Ring Road Connector",
        coordinates: [
            [12.3360, 76.6210],
            [12.3315, 76.6270],
            [12.3190, 76.6450],
            [12.3140, 76.6320]
        ],
        base_pci: 52.0,
        decay_rate_k: 0.016,
        distress_items: ["2 Severe Potholes (8.6cm)", "1 Longitudinal Fissure"]
    },
    {
        corridor_id: "CORR-05",
        name: "Hebbal Flyover ↔ Manyata Tech Park North Corridor",
        jurisdiction: "BBMP East / Yelahanka",
        arterial_type: "Airport Expressway Feeder",
        coordinates: [
            [13.0358, 77.5970],
            [13.0390, 77.6265],
            [13.0450, 77.6205],
            [13.0485, 77.6240]
        ],
        base_pci: 82.0,
        decay_rate_k: 0.009,
        distress_items: ["1 Minor Transverse Crack (Repaired)"]
    }
];

function calculatePciDecay(basePci, decayK, days) {
    const projected = basePci * Math.exp(-decayK * days);
    return Math.round(Math.max(10.0, Math.min(100.0, projected)) * 10) / 10;
}

function getPciCategory(pci) {
    if (pci >= 80.0) {
        return { band: "GOOD", color: "#10B981", treatment: "Routine Slurry Seal & Sweeping (Preventive)" };
    } else if (pci >= 65.0) {
        return { band: "FAIR", color: "#FBBF24", treatment: "Polymeric Crack Sealing per CPWD SOR 14.1" };
    } else if (pci >= 40.0) {
        return { band: "POOR", color: "#F97316", treatment: "Milled Cold Mastic Patch per CPWD SOR 16.2.2" };
    } else {
        return { band: "CRITICAL", color: "#EF4444", treatment: "Emergency Base-Course Full-Depth Overhaul" };
    }
}

function renderPCIHeatmap(days = 0) {
    if (!state.map) return;
    if (!state.pciLayerGroup) {
        state.pciLayerGroup = L.layerGroup().addTo(state.map);
    } else {
        state.pciLayerGroup.clearLayers();
    }

    fetch(`/api/pci-heatmap?days=${days}`)
        .then(res => {
            if (!res.ok) throw new Error("API Offline");
            return res.json();
        })
        .then(corridors => {
            drawCorridors(corridors, days);
        })
        .catch(() => {
            const fallbackCorridors = FALLBACK_PCI_CORRIDORS.map(c => {
                const projected = calculatePciDecay(c.base_pci, c.decay_rate_k, days);
                const cat = getPciCategory(projected);
                return {
                    corridor_id: c.corridor_id,
                    name: c.name,
                    jurisdiction: c.jurisdiction,
                    arterial_type: c.arterial_type,
                    coordinates: c.coordinates,
                    base_pci: c.base_pci,
                    projected_pci: projected,
                    forecast_days: days,
                    rating_band: cat.band,
                    color: cat.color,
                    recommended_treatment: cat.treatment,
                    distress_items: c.distress_items
                };
            });
            drawCorridors(fallbackCorridors, days);
        });
}

function drawCorridors(corridors, days) {
    corridors.forEach(c => {
        const polyline = L.polyline(c.coordinates, {
            color: c.color,
            weight: 6,
            opacity: 0.88,
            lineJoin: 'round',
            dashArray: days > 0 && c.projected_pci < 50 ? '8, 8' : null
        });

        const popupContent = `
            <div style="color:#0F172A; font-family:'Plus Jakarta Sans',sans-serif; min-width:220px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <span style="font-weight:800; font-size:12px; color:${c.color};">${c.corridor_id} • [${c.rating_band}]</span>
                    <span style="background:${c.color}; color:#fff; font-weight:800; font-size:10px; padding:2px 6px; border-radius:4px;">PCI: ${c.projected_pci}/100</span>
                </div>
                <div style="font-size:11px; font-weight:700; margin-bottom:4px;">${c.name}</div>
                <div style="font-size:10px; color:#64748B; margin-bottom:2px;">Jurisdiction: <b>${c.jurisdiction}</b></div>
                <div style="font-size:10px; color:#64748B; margin-bottom:2px;">Baseline PCI: <b>${c.base_pci}</b> ${days > 0 ? `➔ Day +${days} Decay: <b style="color:${c.color};">${c.projected_pci}</b>` : ''}</div>
                <div style="font-size:10px; color:#475569; margin-top:4px; padding-top:4px; border-top:1px solid #E2E8F0;">
                    <b>ASTM Action:</b> ${c.recommended_treatment}
                </div>
            </div>
        `;

        polyline.bindPopup(popupContent);
        polyline.addTo(state.pciLayerGroup);
    });
}

// 3. Live Edge Dashcam Vision Canvas Simulator
function initDashcamSimulator() {
    const canvas = document.getElementById('dashcam-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let frameCount = 0;
    const baseImage = new Image();
    baseImage.src = 'image1.jpg';

    function drawFrame() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw camera frame or synthetic road gradient
        if (baseImage.complete && baseImage.naturalWidth > 0) {
            ctx.drawImage(baseImage, 0, 0, canvas.width, canvas.height);
        } else {
            // High-tech fallback canvas road simulation
            const grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
            grad.addColorStop(0, '#1E293B');
            grad.addColorStop(0.5, '#0F172A');
            grad.addColorStop(1, '#05070D');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Road perspective lines
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(canvas.width * 0.45, canvas.height * 0.4);
            ctx.lineTo(canvas.width * 0.1, canvas.height);
            ctx.moveTo(canvas.width * 0.55, canvas.height * 0.4);
            ctx.lineTo(canvas.width * 0.9, canvas.height);
            ctx.stroke();
        }

        // Animated bounding boxes (YOLOv8 Detection Overlays)
        const timeOsc = Math.sin(frameCount * 0.05);

        // 1. Pothole Bounding Box (Amber)
        const potX = canvas.width * 0.58 + timeOsc * 2;
        const potY = canvas.height * 0.62;
        const potW = 140;
        const potH = 65;

        ctx.strokeStyle = '#FF5E1E';
        ctx.lineWidth = 2.5;
        ctx.strokeRect(potX, potY, potW, potH);

        // Label Tag
        ctx.fillStyle = '#FF5E1E';
        ctx.fillRect(potX, potY - 20, 130, 20);
        ctx.fillStyle = '#FFFFFF';
        ctx.font = 'bold 9px "JetBrains Mono"';
        ctx.fillText('POTHOLE | 96.4%', potX + 5, potY - 6);

        // 2. Waterlogging Bounding Box (Cyan)
        const watX = canvas.width * 0.22 - timeOsc * 2;
        const watY = canvas.height * 0.52;
        const watW = 160;
        const watH = 60;

        ctx.strokeStyle = '#00E5FF';
        ctx.lineWidth = 2;
        ctx.strokeRect(watX, watY, watW, watH);

        ctx.fillStyle = '#00E5FF';
        ctx.fillRect(watX, watY - 20, 150, 20);
        ctx.fillStyle = '#090D16';
        ctx.font = 'bold 9px "JetBrains Mono"';
        ctx.fillText('WATERLOGGING | 25m', watX + 5, watY - 6);

        // Privacy Blur Simulation Box (Face & Plate Masking)
        if (state.settings.privacyBlur) {
            const blurX = canvas.width * 0.12;
            const blurY = canvas.height * 0.45;
            const blurW = 35;
            const blurH = 45;

            // Simulated pixelation
            ctx.fillStyle = 'rgba(100, 116, 139, 0.85)';
            ctx.fillRect(blurX, blurY, blurW, blurH);
            ctx.strokeStyle = '#10B981';
            ctx.lineWidth = 1;
            ctx.strokeRect(blurX, blurY, blurW, blurH);

            ctx.fillStyle = '#10B981';
            ctx.font = '7px "JetBrains Mono"';
            ctx.fillText('DPDP BLUR', blurX, blurY - 4);
        }

        frameCount++;
        requestAnimationFrame(drawFrame);
    }

    drawFrame();
}

// 4. Activity Log Feed
function initEventLogFeed() {
    const feed = document.getElementById('activity-feed');
    if (!feed) return;
    feed.innerHTML = state.logs.map(log => `
        <div class="log-entry">
            <span class="log-time">${log.time}</span>
            <span class="log-agent">${log.agent}:</span>
            <span>${log.text}</span>
        </div>
    `).join('');
}

function pushLog(agent, text) {
    const now = new Date();
    const timeStr = now.toTimeString().split(' ')[0];
    state.logs.unshift({ time: timeStr, agent, text });
    if (state.logs.length > 30) state.logs.pop();
    initEventLogFeed();
}

// 5. Interactive Action Listeners
function initActionListeners() {
    // 1. Simulate Detection Button
    const btnDetect = document.getElementById('btn-simulate-detect');
    if (btnDetect) {
        btnDetect.addEventListener('click', () => {
            pushLog("Agent 1: Vision Perception", "Spotted critical POTHOLE (depth: 9.8cm) on Sarjapur Outer Ring Road. Transmitting <12KB GeoJSON.");
            highlightAgent(1);

            setTimeout(() => {
                pushLog("Agent 2: Geo-Spatial Clustering", "DBSCAN matched coordinates to existing cluster #DBSCAN-CL-041 (15th verified pass).");
                highlightAgent(2);
            }, 600);

            setTimeout(() => {
                const newTicket = `PWD-OCT-${Math.floor(1000 + Math.random() * 9000)}`;
                pushLog("Agent 3: Municipal Dispatch", `Auto-filed PWD Work Order #${newTicket} to BBMP Mahadevapura Ward portal. SLA: <48h.`);
                highlightAgent(3);
                addNewWorkOrder(newTicket, "POTHOLE", "CRITICAL_P1", "Sarjapur Outer Ring Road", 15);
            }, 1200);

            setTimeout(() => {
                pushLog("Agent 4: Fleet Advisory", "Broadcasted WebSocket detour alert to 6 upstream buses approaching Sarjapur junction.");
                highlightAgent(4);
                triggerDriverAlert("CRITICAL POTHOLE (9.8cm Depth)", "Sarjapur-ORR Junction (180m Ahead)", "Left lane merge recommended");
            }, 1800);
        });
    }

    // 2. Trigger Driver Alert Direct Button
    const btnAlert = document.getElementById('btn-driver-alert');
    if (btnAlert) {
        btnAlert.addEventListener('click', () => {
            triggerDriverAlert("CRITICAL POTHOLE", "VVCE Ring Road Junction (150m Ahead)", "Slow down to 20 km/h; move to center lane");
        });
    }

    // 3. Modal Close
    const modalClose = document.getElementById('modal-close-btn');
    const modalOverlay = document.getElementById('driver-alert-modal');
    if (modalClose && modalOverlay) {
        modalClose.addEventListener('click', () => {
            modalOverlay.classList.remove('show');
        });
    }

    // 4. Privacy Toggle
    const btnPrivacy = document.getElementById('btn-toggle-privacy');
    if (btnPrivacy) {
        btnPrivacy.addEventListener('click', () => {
            state.settings.privacyBlur = !state.settings.privacyBlur;
            btnPrivacy.textContent = state.settings.privacyBlur ? "Privacy Blur: ON" : "Privacy Blur: OFF";
            btnPrivacy.classList.toggle('btn-secondary', state.settings.privacyBlur);
            pushLog("Privacy Guard", `DPDP On-Device Gaussian Blur toggled ${state.settings.privacyBlur ? 'ENABLED' : 'DISABLED'}.`);
        });
    }

    // 5. ASTM D6433 PCI Predictive Degradation Buttons
    const decayButtons = [
        { id: 'btn-decay-0', days: 0 },
        { id: 'btn-decay-14', days: 14 },
        { id: 'btn-decay-30', days: 30 }
    ];

    decayButtons.forEach(btnInfo => {
        const btn = document.getElementById(btnInfo.id);
        if (btn) {
            btn.addEventListener('click', () => {
                decayButtons.forEach(b => {
                    const el = document.getElementById(b.id);
                    if (el) el.classList.toggle('active', b.id === btnInfo.id);
                });
                renderPCIHeatmap(btnInfo.days);
                pushLog("PCI Forecast Engine", `Markov Chain degradation projection computed for Day +${btnInfo.days}. Road surface colors updated.`);
            });
        }
    });

}

function highlightAgent(stepNumber) {
    for (let i = 1; i <= 4; i++) {
        const el = document.getElementById(`agent-step-${i}`);
        if (el) el.classList.toggle('active', i === stepNumber);
    }
}

function addNewWorkOrder(ticket, type, sev, loc, passes) {
    state.workOrders.unshift({
        ticket, type, sev, loc, passes, sla: "47h 58m remaining", status: "DISPATCHED"
    });
    renderWorkOrdersTable();
}

function renderWorkOrdersTable() {
    const tbody = document.getElementById('work-orders-tbody');
    if (!tbody) return;
    tbody.innerHTML = state.workOrders.map(w => `
        <tr>
            <td><strong style="color:#00E5FF;">${w.ticket}</strong></td>
            <td><span class="pill-tag ${w.sev.includes('CRITICAL') ? 'pill-orange' : 'pill-cyan'}">${w.type}</span></td>
            <td>${w.loc}</td>
            <td><strong>${w.passes} passes</strong></td>
            <td><span style="color:#10B981;">${w.sla}</span></td>
            <td><span class="pill-tag pill-cyan">${w.status}</span></td>
        </tr>
    `).join('');
}

function triggerDriverAlert(hazard, loc, advice) {
    const modal = document.getElementById('driver-alert-modal');
    const titleEl = document.getElementById('driver-alert-title');
    const locEl = document.getElementById('driver-alert-loc');
    const adviceEl = document.getElementById('driver-alert-advice');

    if (titleEl) titleEl.textContent = hazard;
    if (locEl) locEl.textContent = loc;
    if (adviceEl) adviceEl.textContent = advice;

    if (modal) modal.classList.add('show');
}

// 6. Polling Bus Movement Simulation
function startRealtimePolling() {
    setInterval(() => {
        state.buses.forEach(b => {
            b.lat += (Math.random() - 0.5) * 0.0006;
            b.lng += (Math.random() - 0.5) * 0.0006;
            if (b.marker) {
                b.marker.setLatLng([b.lat, b.lng]);
            }
        });
    }, 3000);
}
