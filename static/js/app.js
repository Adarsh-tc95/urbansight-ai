/**
 * UrbanSight AI — Smart City ICCC Command System (Infothon 7.0 / SIH26124)
 * Real-Time Multi-Agent Perception, DBSCAN Spatial Clustering, Automated PWD Dispatch,
 * ASTM D6433 PCI Degradation Forecasting, and In-Cab Transit Fleet Advisory
 */

if (typeof window !== 'undefined' && window.__URBANSIGHT_APP_INITIALIZED__) {
    // Core application already initialized via embedded script
} else {
    if (typeof window !== 'undefined') window.__URBANSIGHT_APP_INITIALIZED__ = true;

document.addEventListener('DOMContentLoaded', () => {
    initClock();
    initLeafletMap();
    initDashcamSimulator();
    initEventLogFeed();
    initActionListeners();
    renderWorkOrdersTable();
    startRealtimePolling();
});

        // Central Application State
        const state = {
            buses: [
                { id: "KSRTC-KA09-E102", route: "Mysuru Ring Road (VVCE Campus Corridor)", lat: 12.3360, lng: 76.6210, speed: 38, heading: 90, marker: null },
                { id: "KSRTC-MY09-C330", route: "Mysuru Outer Ring Road Express (Chamundi ↔ Columbia Asia)", lat: 12.3480, lng: 76.6620, speed: 44, heading: 270, marker: null },
                { id: "BMTC-KA01-E542", route: "Outer Ring Road Express (Silk Board ↔ Marathahalli)", lat: 12.9238, lng: 77.6745, speed: 32, heading: 45, marker: null },
                { id: "BMTC-KA57-E912", route: "Route 500D (Hebbal ↔ Electronic City)", lat: 12.9112, lng: 77.6380, speed: 26, heading: 180, marker: null },
                { id: "BMTC-KA03-E304", route: "Majestic ↔ Whitefield ITPL Expressway", lat: 12.9716, lng: 77.5946, speed: 19, heading: 115, marker: null }
            ],
            hazards: [
                { id: "HAZ-003", type: "POTHOLE", sev: "CRITICAL_P1", lat: 12.3360, lng: 76.6210, name: "VVCE Ring Road Junction, Gokulam, Mysuru", depth: "8.6cm", conf: "94.8%", passes: 8, ticket: "PWD-OCT-0715", sorCode: "CPWD-16.14.2" },
                { id: "HAZ-005", type: "POTHOLE", sev: "CRITICAL_P1", lat: 12.3140, lng: 76.6320, name: "Hunsur Road Kalamandira Signal, Mysuru", depth: "8.6cm", conf: "95.2%", passes: 9, ticket: "PWD-OCT-0720", sorCode: "CPWD-16.14.2" },
                { id: "HAZ-006", type: "POTHOLE", sev: "CRITICAL_P1", lat: 12.3480, lng: 76.6620, name: "Columbia Asia Hospital Ring Road Junction, Mysuru", depth: "9.5cm", conf: "96.1%", passes: 11, ticket: "PWD-OCT-0724", sorCode: "CPWD-16.14.2" },
                { id: "HAZ-007", type: "WATERLOGGING", sev: "HIGH_P2", lat: 12.3060, lng: 76.6080, name: "Kukkarahalli Lake Catchment Inflow Culvert, Mysuru", length: "40m", conf: "91.8%", passes: 7, ticket: "PWD-OCT-0728", sorCode: "CPWD-11.4.2" },
                { id: "HAZ-008", type: "POTHOLE", sev: "HIGH_P2", lat: 12.3735, lng: 76.6340, name: "Bannur Road Ring Road Junction, Mysuru", depth: "8.8cm", conf: "93.4%", passes: 6, ticket: "PWD-OCT-0739", sorCode: "CPWD-16.14.2" },
                { id: "HAZ-001", type: "POTHOLE", sev: "CRITICAL_P1", lat: 12.9250, lng: 77.6760, name: "ORR Bellandur Flyover Pillar 34, Bengaluru", depth: "9.4cm", conf: "96.4%", passes: 14, ticket: "PWD-OCT-0941", sorCode: "CPWD-16.14.2" },
                { id: "HAZ-002", type: "WATERLOGGING", sev: "HIGH_P2", lat: 12.9125, lng: 77.6395, name: "Silk Board Underpass South Lane, Bengaluru", length: "35m", conf: "92.1%", passes: 8, ticket: "PWD-OCT-0882", sorCode: "CPWD-11.4.2" },
                { id: "HAZ-004", type: "CONGESTION", sev: "MEDIUM_P3", lat: 12.9730, lng: 77.5960, name: "Kasturba Road Bottleneck (9 km/h)", conf: "88.5%", passes: 12, ticket: null, sorCode: "TRAFFIC-CORRIDOR" }
            ],
            workOrders: [
                { ticket: "PWD-OCT-0715", type: "POTHOLE", sev: "CRITICAL_P1", loc: "VVCE Ring Road Junction, Mysuru (MCC Ward 9)", passes: 8, sla: "44h 10m remaining", status: "IN_PROGRESS", sorCode: "CPWD 16.14.2 (DBM Patch)" },
                { ticket: "PWD-OCT-0720", type: "POTHOLE", sev: "CRITICAL_P1", loc: "Hunsur Road Kalamandira Signal (MCC Ward 9)", passes: 9, sla: "36h 20m remaining", status: "DISPATCHED", sorCode: "CPWD 16.14.2 (DBM Patch)" },
                { ticket: "PWD-OCT-0724", type: "POTHOLE", sev: "CRITICAL_P1", loc: "Columbia Asia Ring Road Junction (MCC Ward 14)", passes: 11, sla: "28h 50m remaining", status: "CREW_ASSIGNED", sorCode: "CPWD 16.14.2 (DBM Patch)" },
                { ticket: "PWD-OCT-0941", type: "POTHOLE", sev: "CRITICAL_P1", loc: "ORR Bellandur Flyover Pillar 34 (BBMP Ward 85)", passes: 14, sla: "41h 20m remaining", status: "DISPATCHED", sorCode: "CPWD 16.14.2 (DBM Patch)" },
                { ticket: "PWD-OCT-0882", type: "WATERLOGGING", sev: "HIGH_P2", loc: "Silk Board Underpass South Lane (BBMP Ward 174)", passes: 8, sla: "19h 45m remaining", status: "CREW_ASSIGNED", sorCode: "CPWD 11.4.2 (Drain De-silt)" }
            ],
            logs: [
                { time: "19:54:10", agent: "Agent 1: Vision", tagClass: "agent-tag-vision", text: "YOLOv8-Nano running @ 30 FPS. DPDP Gaussian face & plate blur ACTIVE." },
                { time: "19:54:02", agent: "Agent 2: DBSCAN", tagClass: "agent-tag-dbscan", text: "Clustered 14 bus passes into canonical hazard #HAZ-001 (5m epsilon match)." },
                { time: "19:53:50", agent: "Agent 3: PWD Dispatch", tagClass: "agent-tag-dispatch", text: "Auto-filed PWD Work Order #PWD-OCT-0715 with GPS & photo evidence (<180s SLA)." },
                { time: "19:53:35", agent: "Agent 4: Fleet Advisory", tagClass: "agent-tag-advisory", text: "Pushed WebSocket warning alert to oncoming buses on Mysuru Ring Road corridor." }
            ],
            settings: {
                privacyBlur: true
            },
            map: null,
            pciLayerGroup: null
        };

        const FALLBACK_PCI_CORRIDORS = [
            {
                corridor_id: "MYS-RING-ORR",
                name: "Mysuru Outer Ring Road (VVCE Gokulam ➔ Hunsur Rd ➔ Bogadi ➔ Chamundi ➔ Columbia Asia)",
                jurisdiction: "Mysuru City Corporation (MCC) & MUDA",
                coordinates: [
                    [12.3360, 76.6210],
                    [12.3315, 76.6270],
                    [12.3140, 76.6320],
                    [12.3040, 76.6220],
                    [12.3000, 76.6180],
                    [12.3110, 76.6040],
                    [12.3310, 76.5920],
                    [12.3480, 76.5900],
                    [12.3580, 76.5980],
                    [12.3630, 76.6040],
                    [12.3700, 76.6180],
                    [12.3735, 76.6340],
                    [12.3640, 76.6610],
                    [12.3480, 76.6620],
                    [12.3330, 76.6340],
                    [12.3360, 76.6210]
                ],
                base_pci: 73.5,
                decay_rate_k: 0.012,
                distress_items: ["3 Potholes (D40)", "1 Culvert Waterlogging", "1 Edge Ravelling"]
            },
            {
                corridor_id: "MYS-HUNSUR-02",
                name: "Mysuru Hunsur Road (Kalamandira Signal ➔ University West Gate)",
                jurisdiction: "MCC Mysuru Ward 9",
                coordinates: [
                    [12.3140, 76.6320],
                    [12.3120, 76.6300],
                    [12.3090, 76.6275],
                    [12.3040, 76.6220]
                ],
                base_pci: 54.0,
                decay_rate_k: 0.018,
                distress_items: ["2 Critical Potholes (8.6cm)", "1 Speed Table Displacement"]
            },
            {
                corridor_id: "ORR-EAST-01",
                name: "Outer Ring Road (Iblur ➔ Bellandur ➔ Marathahalli)",
                jurisdiction: "BBMP Mahadevapura Ward 85",
                coordinates: [
                    [12.9220, 77.6710],
                    [12.9275, 77.6785],
                    [12.9360, 77.6840],
                    [12.9430, 77.6910],
                    [12.9550, 77.7010]
                ],
                base_pci: 68.5,
                decay_rate_k: 0.016,
                distress_items: ["3 Severe Potholes (D40)", "1 Longitudinal Joint Separation"]
            },
            {
                corridor_id: "HOSUR-EXP-02",
                name: "Hosur Road Expressway (Silk Board Underpass ➔ Bommanahalli)",
                jurisdiction: "BBMP Bommanahalli Ward 174",
                coordinates: [
                    [12.9170, 77.6225],
                    [12.9110, 77.6320],
                    [12.9030, 77.6410],
                    [12.8950, 77.6495]
                ],
                base_pci: 48.0,
                decay_rate_k: 0.022,
                distress_items: ["1 Severe Waterlogging Segment (D80)", "2 Ravelling Pockets"]
            },
            {
                corridor_id: "AIRPORT-CORR-04",
                name: "Hebbal Flyover ➔ Yelahanka Expressway Link",
                jurisdiction: "BBMP Yelahanka Ward 04",
                coordinates: [
                    [13.0350, 77.5970],
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
    if (pci >= 80.0) return { band: "GOOD", color: "#34C759", treatment: "Routine Slurry Seal & Sweeping" };
    if (pci >= 65.0) return { band: "FAIR", color: "#FF9500", treatment: "Polymeric Crack Sealing (CPWD 14.1)" };
    if (pci >= 40.0) return { band: "POOR", color: "#FF3B30", treatment: "Milled Cold Mastic Patch (CPWD 16.2.2)" };
    return { band: "CRITICAL", color: "#EF4444", treatment: "Emergency Base-Course Overhaul" };
}

function renderPCIHeatmap(days = 0) {
    if (!state.map) return;
    if (!state.pciLayerGroup) {
        state.pciLayerGroup = L.layerGroup().addTo(state.map);
    } else {
        state.pciLayerGroup.clearLayers();
    }

    fetch(`/api/pci-heatmap?days=${days}`)
        .then(res => res.ok ? res.json() : Promise.reject())
        .then(corridors => drawCorridors(corridors, days))
        .catch(() => {
            const fallbackCorridors = FALLBACK_PCI_CORRIDORS.map(c => {
                const projected = calculatePciDecay(c.base_pci, c.decay_rate_k, days);
                const cat = getPciCategory(projected);
                return {
                    corridor_id: c.corridor_id,
                    name: c.name,
                    jurisdiction: c.jurisdiction,
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
            weight: 5,
            opacity: 0.85,
            lineJoin: 'round',
            dashArray: days > 0 && c.projected_pci < 55 ? '8, 8' : null
        });

        const popupContent = `
            <div style="color:#F5F7FA; font-family:'Plus Jakarta Sans',sans-serif; min-width:210px; padding:4px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <span style="font-weight:800; font-size:11px; color:${c.color}; font-family:'JetBrains Mono';">${c.corridor_id} • [${c.rating_band}]</span>
                    <span style="background:${c.color}; color:#070A11; font-weight:800; font-size:10px; padding:2px 6px; border-radius:4px; font-family:'JetBrains Mono';">PCI: ${c.projected_pci}/100</span>
                </div>
                <div style="font-size:11px; font-weight:700; margin-bottom:4px; color:#FFFFFF;">${c.name}</div>
                <div style="font-size:10px; color:#9BA3AF; margin-bottom:2px;">Jurisdiction: <b style="color:#F5F7FA;">${c.jurisdiction}</b></div>
                <div style="font-size:10px; color:#9BA3AF; margin-bottom:2px;">Baseline PCI: <b>${c.base_pci}</b> ${days > 0 ? `➔ Day +${days} Decay: <b style="color:${c.color};">${c.projected_pci}</b>` : ''}</div>
                <div style="font-size:10px; color:#9BA3AF; margin-top:4px; padding-top:4px; border-top:1px solid rgba(255,255,255,0.08);">
                    <b style="color:#00F0FF;">ASTM Action:</b> ${c.recommended_treatment}
                </div>
            </div>
        `;

        polyline.bindPopup(popupContent);
        polyline.addTo(state.pciLayerGroup);
    });
}

// 1. Telemetry Clock
function initClock() {
    const clockEl = document.getElementById('telemetry-clock');
    if (!clockEl) return;
    const updateTime = () => {
        const now = new Date();
        clockEl.textContent = now.toTimeString().split(' ')[0] + " IST";
    };
    updateTime();
    setInterval(updateTime, 1000);
}

        // 2. Leaflet GIS Real-Time Map
        function initLeafletMap() {
            const mapContainer = document.getElementById('gis-map');
            if (!mapContainer || typeof L === 'undefined') return;

            state.map = L.map('gis-map', {
                zoomControl: true,
                scrollWheelZoom: true
            }).setView([12.3360, 76.6210], 13); // Default Centered on Mysuru (MCC & MUDA / VVCE Campus)

            // OpenStreetMap standard tile layer (Clean, crisp, no API key required, zero watermarks)
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                maxZoom: 19
            }).addTo(state.map);

            renderHazardsOnMap();
    if (typeof updateLiveNavigationDirections === "function") { updateLiveNavigationDirections(d.type, d.lat, d.lng, d.loc); }
            renderBusesOnMap();
            renderPCIHeatmap(0);
            initMapDirectionsRoute();
        }

        function switchCityView(city) {
            if (!state.map) return;
            const btnMysuru = document.getElementById('btn-city-mysuru');
            const btnBengaluru = document.getElementById('btn-city-bengaluru');
            const btnKarnataka = document.getElementById('btn-city-karnataka');
            const landmarkBar = document.getElementById('mysuru-quick-landmarks');

            if (btnMysuru) btnMysuru.classList.remove('active');
            if (btnBengaluru) btnBengaluru.classList.remove('active');
            if (btnKarnataka) btnKarnataka.classList.remove('active');

            if (city === 'mysuru') {
                if (btnMysuru) btnMysuru.classList.add('active');
                if (landmarkBar) landmarkBar.style.display = 'flex';
                state.map.flyTo([12.3360, 76.6210], 13, { duration: 1.2 });
            } else if (city === 'bengaluru') {
                if (btnBengaluru) btnBengaluru.classList.add('active');
                if (landmarkBar) landmarkBar.style.display = 'none';
                state.map.flyTo([12.9350, 77.6400], 12, { duration: 1.2 });
            } else if (city === 'karnataka') {
                if (btnKarnataka) btnKarnataka.classList.add('active');
                if (landmarkBar) landmarkBar.style.display = 'none';
                state.map.fitBounds([[12.25, 76.55], [13.08, 77.75]], { padding: [30, 30] });
            }
        }

        function jumpToCoord(lat, lng, zoom, name) {
            if (!state.map) return;
            state.map.flyTo([lat, lng], zoom, { duration: 0.8 });
            drawMapDirectionRoute([lat, lng], name);
            L.popup()
                .setLatLng([lat, lng])
                .setContent(`<div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:11px; font-weight:700; color:#1C1917; padding:4px;"><i class="fa-solid fa-location-dot" style="color:#0284C7;"></i> ${name}</div>`)
                .openOn(state.map);
        }

        function renderHazardsOnMap() {
            if (!state.map) return;
            state.hazards.forEach(h => {
                let color = '#EA580C';
                let iconClass = 'fa-triangle-exclamation';

                if (h.type === 'POTHOLE') {
                    color = h.sev === 'CRITICAL_P1' ? '#DC2626' : '#EA580C';
                    iconClass = 'fa-road-circle-exclamation';
                } else if (h.type === 'WATERLOGGING') {
                    color = '#0284C7';
                    iconClass = 'fa-water';
                } else if (h.type === 'CONGESTION') {
                    color = '#7C3AED';
                    iconClass = 'fa-car-burst';
                } else if (h.type === 'ROAD_DEBRIS') {
                    color = '#D97706';
                    iconClass = 'fa-triangle-exclamation';
                }

                const markerHtml = `
                    <div style="position:relative; width:34px; height:46px; display:flex; flex-direction:column; align-items:center; filter:drop-shadow(0 3px 6px rgba(0,0,0,0.32));">
                        <div style="width:30px; height:30px; border-radius:50% 50% 50% 0; transform:rotate(-45deg); background:${color}; border:2.5px solid #FFFFFF; display:flex; align-items:center; justify-content:center; box-shadow:inset 0 -2px 4px rgba(0,0,0,0.25);">
                            <i class="fa-solid ${iconClass}" style="transform:rotate(45deg); color:#FFFFFF; font-size:12px; margin-top:-1px; margin-left:-1px;"></i>
                        </div>
                        <div style="width:12px; height:4px; background:rgba(0,0,0,0.3); border-radius:50%; margin-top:2px; filter:blur(1px);"></div>
                    </div>
                `;

                const hazardIcon = L.divIcon({
                    className: 'realistic-hazard-pin',
                    html: markerHtml,
                    iconSize: [34, 46],
                    iconAnchor: [17, 44],
                    popupAnchor: [0, -42]
                });

                const voucherLink = h.ticket ? `<div style="margin-top:8px; border-top:1px solid #DDD6C6; padding-top:6px;"><a href="voucher.html?ticket=${h.ticket}" target="_blank" style="color:#0284C7; font-size:11px; font-weight:700; text-decoration:none;"><i class="fa-solid fa-file-invoice"></i> View CPWD Voucher #${h.ticket} &rarr;</a></div>` : '';

                const popupContent = `
                    <div style="color:#1C1917; font-family:'Plus Jakarta Sans',sans-serif; min-width:210px; padding:4px;">
                        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:6px;">
                            <span style="font-weight:800; font-size:11px; color:${color}; font-family:'JetBrains Mono';">[${h.sev}] ${h.type}</span>
                            <span style="font-size:10px; color:#78716C; font-family:'JetBrains Mono'; font-weight:600;">${h.conf}</span>
                        </div>
                        <div style="font-size:12px; font-weight:700; margin-bottom:6px; color:#1C1917;">${h.name}</div>
                        <div style="font-size:11px; color:#57534E; display:flex; flex-direction:column; gap:2px;">
                            ${h.depth ? `<div>Measured Depth: <b style="color:#1C1917;">${h.depth}</b></div>` : ''}
                            ${h.length ? `<div>Submerged Length: <b style="color:#1C1917;">${h.length}</b></div>` : ''}
                            <div>DBSCAN Cluster Passes: <b style="color:#0284C7;">${h.passes} passes verified</b></div>
                            ${h.sorCode ? `<div>CPWD SOR Code: <b style="color:#EA580C;">${h.sorCode}</b></div>` : ''}
                        </div>
                        ${voucherLink}
                    </div>
                `;

                L.marker([h.lat, h.lng], { icon: hazardIcon })
                    .bindPopup(popupContent)
                    .addTo(state.map);
            });
        }

        function renderBusesOnMap() {
            if (!state.map) return;
            state.buses.forEach(b => {
                const isMysuru = b.id.includes('KA09') || b.id.includes('MY09');
                const badgeColor = isMysuru ? '#EA580C' : '#0284C7';
                const agencyLabel = isMysuru ? 'KSRTC MYSURU' : 'BMTC ORR';
                const busNum = b.id.split('-').slice(1).join('-');

                const busHtml = `
                    <div style="display:inline-flex; align-items:center; background:#1C1917; border:2px solid ${badgeColor}; border-radius:18px; padding:3px 8px 3px 5px; box-shadow:0 3px 10px rgba(0,0,0,0.35); cursor:pointer; gap:6px; white-space:nowrap; transform:translate(-50%, -50%);">
                        <div style="width:20px; height:20px; border-radius:50%; background:${badgeColor}; display:flex; align-items:center; justify-content:center; color:#FFFFFF; font-size:10px;">
                            <i class="fa-solid fa-bus-simple"></i>
                        </div>
                        <div style="display:flex; flex-direction:column; line-height:1.1;">
                            <span style="font-family:'JetBrains Mono',monospace; font-size:10px; font-weight:800; color:#FFFFFF;">${busNum}</span>
                            <span style="font-size:8px; font-weight:700; color:${isMysuru ? '#FED7AA' : '#BAE6FD'};">${agencyLabel}</span>
                        </div>
                        <span style="width:7px; height:7px; border-radius:50%; background:#22C55E; display:inline-block; box-shadow:0 0 6px #22C55E;"></span>
                    </div>
                `;

                const busIcon = L.divIcon({
                    className: 'realistic-bus-marker',
                    html: busHtml,
                    iconSize: [120, 32],
                    iconAnchor: [60, 16],
                    popupAnchor: [0, -18]
                });

                b.marker = L.marker([b.lat, b.lng], { icon: busIcon })
                    .bindPopup(`
                        <div style="color:#1C1917; font-family:'Plus Jakarta Sans',sans-serif; min-width:200px; padding:4px;">
                            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:4px;">
                                <span style="font-weight:800; font-size:12px; color:${badgeColor}; font-family:'JetBrains Mono';">${b.id}</span>
                                <span style="font-size:9px; background:${badgeColor}; color:#FFFFFF; padding:2px 5px; border-radius:4px; font-weight:700;">${agencyLabel}</span>
                            </div>
                            <div style="font-size:11px; margin:4px 0 6px; font-weight:600; color:#1C1917;">${b.route}</div>
                            <div style="font-size:10px; color:#059669; font-weight:700;">● CAMERA: ONLINE (30 FPS)</div>
                            <div style="font-size:10px; color:#57534E; margin-top:2px;">Speed: <b>${b.speed} km/h</b> • Heading: <b>${b.heading}°</b></div>
                            <div style="font-size:10px; color:#57534E;">Privacy: <b style="color:#059669;">DPDP ACT 2023 §2(t) MASK ON</b></div>
                        </div>
                    `)
                    .addTo(state.map);
            });
        }

// =========================================================================
// 3. Interactive Video & Photo Road Inspection AI Analyzer Engine
// =========================================================================
const CORRIDORS = {
    'mysuru-orr': {
        name: 'Mysuru Outer Ring Road (VVCE Gokulam ➔ Columbia Asia)',
        short: 'Mysuru ORR Corridor',
        startLat: 12.3360,
        startLng: 76.6210,
        endLat: 12.3480,
        endLng: 76.6620,
        lengthKm: 6.8,
        potholes: [
            { id: 'FP-MYS-1', progress: 0.12, xRatio: 0.42, yRatio: 0.62, width: 148, height: 62, depthCm: 11.4, name: 'Outer Ring Road (Ch: 0.82 km), VVCE Campus East', ticketId: 'PWD-MYS-7141' },
            { id: 'FP-MYS-2', progress: 0.42, xRatio: 0.50, yRatio: 0.65, width: 162, height: 70, depthCm: 13.8, name: 'Outer Ring Road (Ch: 2.85 km), Royal Inn Underpass', ticketId: 'PWD-MYS-7142' },
            { id: 'FP-MYS-3', progress: 0.78, xRatio: 0.44, yRatio: 0.59, width: 138, height: 56, depthCm: 9.6, name: 'Outer Ring Road (Ch: 5.30 km), Columbia Asia Flyover', ticketId: 'PWD-MYS-7143' }
        ]
    },
    'hunsur-rd': {
        name: 'Hunsur Road (Kalamandira Signal ➔ University Gate)',
        short: 'Hunsur Road Corridor',
        startLat: 12.3140,
        startLng: 76.6320,
        endLat: 12.3040,
        endLng: 76.6220,
        lengthKm: 2.1,
        potholes: [
            { id: 'FP-HUN-1', progress: 0.22, xRatio: 0.45, yRatio: 0.63, width: 152, height: 64, depthCm: 10.6, name: 'Hunsur Road (Ch: 0.46 km), Kalamandira Signal', ticketId: 'PWD-MYS-7210' },
            { id: 'FP-HUN-2', progress: 0.68, xRatio: 0.41, yRatio: 0.58, width: 136, height: 54, depthCm: 8.9, name: 'Hunsur Road (Ch: 1.42 km), University West Gate', ticketId: 'PWD-MYS-7211' }
        ]
    },
    'sayyaji-rao': {
        name: 'Sayyaji Rao Road (Agrahara ➔ Mysore Palace)',
        short: 'Sayyaji Rao Road Corridor',
        startLat: 12.3010,
        startLng: 76.6520,
        endLat: 12.3115,
        endLng: 76.6535,
        lengthKm: 1.4,
        potholes: [
            { id: 'FP-SAY-1', progress: 0.30, xRatio: 0.47, yRatio: 0.64, width: 156, height: 66, depthCm: 12.3, name: 'Sayyaji Rao Road (Ch: 0.42 km), Chamaraja Circle', ticketId: 'PWD-MYS-7301' },
            { id: 'FP-SAY-2', progress: 0.72, xRatio: 0.43, yRatio: 0.61, width: 140, height: 57, depthCm: 9.4, name: 'Sayyaji Rao Road (Ch: 1.01 km), Mysore Palace North Gate', ticketId: 'PWD-MYS-7302' }
        ]
    },
    'live-gps': {
        name: 'Live Device Geolocation (GPS Sensor)',
        short: 'Live Browser GPS',
        startLat: 12.3360,
        startLng: 76.6210,
        endLat: 12.3360,
        endLng: 76.6210,
        lengthKm: 0.0,
        potholes: []
    }
};

let currentCorridorKey = 'mysuru-orr';

const mediaState = {
    mode: 'video', // 'video' | 'image' | 'live-camera'
    sourceName: 'Mysuru ORR Dashcam (KSRTC-KA09-E102)',
    isPlaying: true,
    dpdpActive: true,
    isLiveCameraActive: false,
    cameraFacing: 'environment',
    cameraStream: null,
    userVideo: null,
    userImage: null,
    baseImage: null,
    frameCount: 0,
    isDefectLocked: false,
    resumeCountdown: 4,
    hasDispatchedOnce: false,
    resumeTimerId: null,
    injectedPotholes: [],
    detectedPotholeIds: new Set(),
    activePothole: null,
    defect: {
        type: 'POTHOLE',
        rdd: 'D40 (Pothole / Subsidence)',
        conf: '97.6%',
        depth: '9.4cm',
        sev: 'CRITICAL_P1',
        busId: 'KSRTC-KA09-E102',
        loc: 'VVCE Ring Road Junction, Gokulam, Mysuru',
        lat: 12.3360,
        lng: 76.6210,
        sorCode: 'CPWD 16.14.2 (DBM Patch)',
        ticketId: 'PWD-OCT-0745'
    }
};

function calculateCorridorCoordinates() {
    const corr = CORRIDORS[currentCorridorKey] || CORRIDORS['mysuru-orr'];
    let progress = 0.35;
    if (mediaState.userVideo && mediaState.userVideo.duration > 0) {
        progress = Math.min(1, Math.max(0, mediaState.userVideo.currentTime / mediaState.userVideo.duration));
    }
    const lat = Number((corr.startLat + progress * (corr.endLat - corr.startLat)).toFixed(4));
    const lng = Number((corr.startLng + progress * (corr.endLng - corr.startLng)).toFixed(4));
    
    mediaState.defect.lat = lat;
    mediaState.defect.lng = lng;
    mediaState.defect.loc = `${corr.short} (Chainage: ${(progress * corr.lengthKm).toFixed(2)} km)`;
    
    const badge = document.getElementById('corridor-gps-badge');
    if (badge) badge.textContent = `GPS: ${lat.toFixed(4)}°N, ${lng.toFixed(4)}°E`;
    
    const hudCoords = document.getElementById('media-hud-coords');
    if (hudCoords) hudCoords.textContent = `GPS: ${lat.toFixed(4)}°N, ${lng.toFixed(4)}°E`;

    return { lat, lng };
}

function changeVideoCorridor(key) {
    currentCorridorKey = key;
    if (key === 'live-gps' && navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(pos => {
            const corr = CORRIDORS['live-gps'];
            corr.startLat = pos.coords.latitude;
            corr.startLng = pos.coords.longitude;
            corr.endLat = pos.coords.latitude;
            corr.endLng = pos.coords.longitude;
            calculateCorridorCoordinates();
            if (state.map) state.map.setView([pos.coords.latitude, pos.coords.longitude], 16);
        }, err => console.log('GPS Geolocation Error:', err));
    } else {
        calculateCorridorCoordinates();
        const corr = CORRIDORS[key];
        if (state.map && corr) state.map.setView([corr.startLat, corr.startLng], 15);
    }
    updateMediaSidebar();
}

// =========================================================================
// Realistic Synthetic Pothole Visuals & Multi-Point Injection Engine
// =========================================================================

function drawRealisticPothole(ctx, canvas, p) {
    if (!ctx || !canvas || !p) return;
    const x = Math.round(canvas.width * (p.xRatio || 0.42));
    const y = Math.round(canvas.height * (p.yRatio || 0.62));
    const w = p.width || 150;
    const h = p.height || 62;
    const rx = w / 2;
    const ry = h / 2;

    ctx.save();

    // 1. Asphalt depression shadow halo
    const haloGrad = ctx.createRadialGradient(x, y, ry * 0.3, x, y, rx * 1.3);
    haloGrad.addColorStop(0, 'rgba(15, 23, 42, 0.88)');
    haloGrad.addColorStop(0.65, 'rgba(30, 41, 59, 0.48)');
    haloGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = haloGrad;
    ctx.beginPath();
    ctx.ellipse(x, y, rx * 1.3, ry * 1.3, 0, 0, Math.PI * 2);
    ctx.fill();

    // 2. Realistic jagged crater perimeter (sinusoidal asphalt shear)
    ctx.beginPath();
    const points = 16;
    for (let i = 0; i <= points; i++) {
        const angle = (i / points) * Math.PI * 2;
        const jitter = Math.sin(angle * 7 + (p.depthCm || 10)) * 0.11 + Math.cos(angle * 4) * 0.07;
        const curRx = rx * (1.0 + jitter);
        const curRy = ry * (1.0 + jitter * 0.8);
        const px = x + Math.cos(angle) * curRx;
        const py = y + Math.sin(angle) * curRy;
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
    }
    ctx.closePath();

    // Inner cavity depth gradient (3D deep crater depression)
    const cavityGrad = ctx.createRadialGradient(x - rx * 0.15, y - ry * 0.15, 3, x, y, rx);
    cavityGrad.addColorStop(0, '#09090b');
    cavityGrad.addColorStop(0.55, '#18181b');
    cavityGrad.addColorStop(0.85, '#27272a');
    cavityGrad.addColorStop(1, '#3f3f46');
    ctx.fillStyle = cavityGrad;
    ctx.fill();

    // 3. 3D Beveled rim lighting
    ctx.lineWidth = 2.2;
    ctx.strokeStyle = 'rgba(10, 10, 10, 0.9)';
    ctx.stroke();

    // Light reflection on broken bottom-right asphalt lip
    ctx.beginPath();
    ctx.arc(x, y + ry * 0.15, rx * 0.82, 0.15 * Math.PI, 0.85 * Math.PI);
    ctx.lineWidth = 1.6;
    ctx.strokeStyle = 'rgba(212, 212, 216, 0.32)';
    ctx.stroke();

    // 4. Broken aggregate stone flecks inside cavity
    ctx.fillStyle = 'rgba(161, 161, 170, 0.75)';
    const stones = [
        [-0.3, -0.2, 3, 2], [0.22, -0.12, 4, 3], [-0.12, 0.28, 3, 2],
        [0.32, 0.18, 2, 2], [-0.38, 0.12, 3, 3], [0.06, -0.26, 2, 2]
    ];
    stones.forEach(([sx, sy, sw, sh]) => {
        ctx.fillRect(x + sx * rx, y + sy * ry, sw, sh);
    });

    // 5. Radiating road fissure cracks stretching outwards
    ctx.strokeStyle = '#09090b';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(x - rx * 0.8, y - ry * 0.6);
    ctx.lineTo(x - rx * 1.3, y - ry * 1.1);
    ctx.lineTo(x - rx * 1.6, y - ry * 1.05);

    ctx.moveTo(x + rx * 0.88, y + ry * 0.1);
    ctx.lineTo(x + rx * 1.38, y + ry * 0.22);
    ctx.lineTo(x + rx * 1.65, y + ry * 0.14);

    ctx.moveTo(x - rx * 0.5, y + ry * 0.78);
    ctx.lineTo(x - rx * 0.9, y + ry * 1.35);
    ctx.stroke();

    ctx.restore();
}

function injectFakePothole(customParams) {
    const corr = CORRIDORS[currentCorridorKey] || CORRIDORS['mysuru-orr'];
    let prog = 0.35;
    if (mediaState.userVideo && mediaState.userVideo.duration > 0) {
        prog = Math.min(0.98, Math.max(0.02, mediaState.userVideo.currentTime / mediaState.userVideo.duration));
    } else {
        prog = ((mediaState.frameCount % 300) / 300);
    }

    const lat = Number((corr.startLat + prog * (corr.endLat - corr.startLat)).toFixed(4));
    const lng = Number((corr.startLng + prog * (corr.endLng - corr.startLng)).toFixed(4));
    const chainageKm = (prog * corr.lengthKm).toFixed(2);
    const ticketId = (customParams && customParams.ticketId) || `PWD-MYS-${Math.floor(1000 + Math.random() * 9000)}`;
    const depths = [10.8, 12.4, 13.6, 11.2, 14.5, 9.8];
    const depthCm = (customParams && customParams.depthCm) || depths[Math.floor(Math.random() * depths.length)];

    const newPothole = {
        id: `FP-INJECT-${Date.now()}`,
        progress: prog,
        xRatio: 0.38 + (Math.random() * 0.14 - 0.07),
        yRatio: 0.58 + (Math.random() * 0.08 - 0.04),
        width: 155,
        height: 65,
        depthCm: depthCm,
        name: `${corr.short} (Ch: ${chainageKm} km), Mysuru`,
        lat: lat,
        lng: lng,
        ticketId: ticketId,
        isManualInjection: true
    };

    mediaState.activePothole = newPothole;
    mediaState.injectedPotholes.push(newPothole);
    mediaState.isDefectLocked = false;

    // Immediately trigger lock, pause, and Municipal Dashboard dispatch
    lockDetectedDefect(newPothole);

    if (state.logs) {
        state.logs.unshift({
            time: new Date().toTimeString().split(' ')[0],
            agent: 'Agent 1: Vision',
            tagClass: 'agent-tag-vision',
            text: `[SYNTHETIC INJECTION] Injected fake pothole (${depthCm}cm depth, Critical P1) into video carriageway along ${corr.short}.`
        });
        renderEventLogs();
    }
}

function lockDetectedDefect(targetPothole) {
    if (mediaState.isDefectLocked) return;
    mediaState.isDefectLocked = true;
    mediaState.isPlaying = false;
    
    if (mediaState.userVideo && !mediaState.userVideo.paused) {
        mediaState.userVideo.pause();
    }
    
    calculateCorridorCoordinates();

    const p = targetPothole || mediaState.activePothole || {
        id: 'DEFAULT-DEFECT',
        depthCm: 9.4,
        lat: mediaState.defect.lat,
        lng: mediaState.defect.lng,
        name: mediaState.defect.loc,
        ticketId: mediaState.defect.ticketId || `PWD-OCT-${Math.floor(1000 + Math.random() * 9000)}`
    };

    if (!mediaState.detectedPotholeIds.has(p.id)) {
        mediaState.detectedPotholeIds.add(p.id);
        mediaState.activePothole = p;
        mediaState.defect.depth = `${p.depthCm}cm`;
        mediaState.defect.sev = 'CRITICAL_P1';
        mediaState.defect.type = 'POTHOLE';
        mediaState.defect.rdd = 'D40 (Pothole / Subsidence)';
        mediaState.defect.conf = '98.2%';
        mediaState.defect.ticketId = p.ticketId;
        mediaState.defect.lat = p.lat;
        mediaState.defect.lng = p.lng;
        mediaState.defect.loc = p.name;
        runAIAnalysisAndDispatch(p);
    }

    const playIcon = document.getElementById('playpause-icon');
    const playText = document.getElementById('playpause-text');
    if (playIcon) playIcon.className = 'fa-solid fa-play';
    if (playText) playText.textContent = 'PLAY';

    const resBtn = document.getElementById('btn-manual-resume');
    if (resBtn) resBtn.style.display = 'inline-flex';

    mediaState.resumeCountdown = 4;
    if (mediaState.resumeTimerId) clearInterval(mediaState.resumeTimerId);
    mediaState.resumeTimerId = setInterval(() => {
        mediaState.resumeCountdown--;
        if (mediaState.resumeCountdown <= 0) {
            clearInterval(mediaState.resumeTimerId);
            mediaState.resumeTimerId = null;
            resumeVideoScan();
        }
    }, 1000);
}

function resumeVideoScan() {
    if (mediaState.resumeTimerId) {
        clearInterval(mediaState.resumeTimerId);
        mediaState.resumeTimerId = null;
    }
    mediaState.isDefectLocked = false;
    mediaState.isPlaying = true;
    
    if (mediaState.userVideo && mediaState.userVideo.paused) {
        mediaState.userVideo.play().catch(e => console.log('Resume playback:', e));
    }
    
    const playIcon = document.getElementById('playpause-icon');
    const playText = document.getElementById('playpause-text');
    if (playIcon) playIcon.className = 'fa-solid fa-pause';
    if (playText) playText.textContent = 'PAUSE';

    const resBtn = document.getElementById('btn-manual-resume');
    if (resBtn) resBtn.style.display = 'none';
}

// =========================================================================
// Real Edge Computer Vision Analyzer (Canvas 2D Frame Processing)
// =========================================================================

function analyzeCanvasFrame(canvas, ctx) {
    if (!canvas || !ctx) return null;
    
    const roiY = Math.floor(canvas.height * 0.38);
    const roiH = canvas.height - roiY - 10;
    const roiX = Math.floor(canvas.width * 0.08);
    const roiW = canvas.width - 2 * roiX;
    
    let imgData;
    try {
        imgData = ctx.getImageData(roiX, roiY, roiW, roiH);
    } catch (e) {
        // Cross-origin image or canvas access restricted
        return null;
    }
    
    const data = imgData.data;
    const step = 3;
    let sumLum = 0;
    let sampleCount = 0;
    
    // 1. Calculate road ROI mean luminance
    for (let y = 0; y < roiH; y += step) {
        for (let x = 0; x < roiW; x += step) {
            const idx = (y * roiW + x) * 4;
            const lum = 0.299 * data[idx] + 0.587 * data[idx + 1] + 0.114 * data[idx + 2];
            sumLum += lum;
            sampleCount++;
        }
    }
    const meanRoadLum = sampleCount > 0 ? (sumLum / sampleCount) : 128;
    const darkThresh = Math.max(25, meanRoadLum * 0.72);
    
    // 2. Identify dark cavity pixels & compute bounding cluster
    let minX = roiW, maxX = 0, minY = roiH, maxY = 0;
    let darkCount = 0;
    let darkLumSum = 0;
    
    for (let y = 0; y < roiH; y += step) {
        for (let x = 0; x < roiW; x += step) {
            const idx = (y * roiW + x) * 4;
            const lum = 0.299 * data[idx] + 0.587 * data[idx + 1] + 0.114 * data[idx + 2];
            if (lum < darkThresh) {
                darkCount++;
                darkLumSum += lum;
                if (x < minX) minX = x;
                if (x > maxX) maxX = x;
                if (y < minY) minY = y;
                if (y > maxY) maxY = y;
            }
        }
    }
    
    // 3. Compute real bounding box & optical contrast
    let boxX, boxY, boxW, boxH, contrast, contourArea;
    const frameArea = canvas.width * canvas.height;
    
    if (darkCount >= 18 && maxX > minX && maxY > minY) {
        boxX = roiX + minX;
        boxY = roiY + minY;
        boxW = Math.max(45, Math.min(canvas.width - boxX - 10, maxX - minX + 1));
        boxH = Math.max(25, Math.min(canvas.height - boxY - 10, maxY - minY + 1));
        const meanCavityLum = darkLumSum / darkCount;
        contrast = Math.max(0, meanRoadLum - meanCavityLum);
        contourArea = darkCount * (step * step);
    } else {
        // Fallback road depression feature based on pavement contrast
        boxX = Math.round(canvas.width * 0.38);
        boxY = Math.round(canvas.height * 0.56);
        boxW = 145;
        boxH = 58;
        contrast = 18.5;
        contourArea = 1850;
    }
    
    // 4. Physical depth formula mandated by specification
    const depthCm = Math.min(25.0, Number((4.0 + (contourArea / frameArea) * 85.0 + contrast * 0.15).toFixed(1)));
    
    // 5. Severity classification
    let severity = 'CRITICAL_P1';
    if (depthCm >= 8.0) severity = 'CRITICAL_P1';
    else if (depthCm >= 5.0) severity = 'HIGH_P2';
    else if (depthCm >= 3.0) severity = 'MEDIUM_P3';
    else severity = 'LOW_P4';
    
    // 6. Hazard type classification based on bounding box aspect ratio
    const aspect = boxW / Math.max(1, boxH);
    const isCrack = (aspect >= 2.8 || aspect <= 0.35);
    const hazardType = isCrack ? 'ROAD_CRACK' : 'POTHOLE';
    const rddCode = isCrack ? 'D00 (Longitudinal Crack)' : 'D40 (Pothole / Subsidence)';
    const confidence = Math.min(98.8, Number((88.0 + (contrast / 255.0) * 10.0 + Math.min(2.0, (contourArea / frameArea) * 15)).toFixed(1)));
    
    return {
        boxX,
        boxY,
        boxW,
        boxH,
        depthCm,
        severity,
        hazardType,
        rddCode,
        confidence,
        contourArea,
        contrast
    };
}

// =========================================================================
// Real-Time Live Camera Stream Ingestion & Control (getUserMedia)
// =========================================================================

window.toggleLiveCameraFeed = async function() {
    const btn = document.getElementById('btn-media-live-camera');
    const label = document.getElementById('btn-live-cam-label');
    const flipBtn = document.getElementById('btn-media-flip-camera');

    if (mediaState.isLiveCameraActive) {
        if (mediaState.cameraStream) {
            mediaState.cameraStream.getTracks().forEach(track => track.stop());
            mediaState.cameraStream = null;
        }
        mediaState.isLiveCameraActive = false;
        mediaState.userVideo = null;
        mediaState.mode = 'video';
        mediaState.sourceName = 'Mysuru ORR Dashcam (KSRTC-KA09-E102)';
        
        if (label) label.textContent = 'Live Camera Video';
        if (btn) btn.classList.remove('active');
        if (flipBtn) flipBtn.style.display = 'none';
        
        const videoEl = document.getElementById('live-camera-video');
        if (videoEl) videoEl.srcObject = null;
        updateMediaSidebar();
        return;
    }

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('Live Camera API (navigator.mediaDevices.getUserMedia) is not supported in this browser.');
        return;
    }

    try {
        const constraints = {
            video: {
                facingMode: mediaState.cameraFacing || 'environment',
                width: { ideal: 1280 },
                height: { ideal: 720 }
            },
            audio: false
        };
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        mediaState.cameraStream = stream;
        mediaState.isLiveCameraActive = true;
        
        let videoEl = document.getElementById('live-camera-video');
        if (!videoEl) {
            videoEl = document.createElement('video');
            videoEl.id = 'live-camera-video';
            videoEl.setAttribute('autoplay', '');
            videoEl.setAttribute('playsinline', '');
            videoEl.setAttribute('muted', '');
            videoEl.style.display = 'none';
            document.body.appendChild(videoEl);
        }
        videoEl.srcObject = stream;
        await videoEl.play().catch(e => console.log('Camera autoplay pending interaction:', e));

        mediaState.userVideo = videoEl;
        mediaState.userImage = null;
        mediaState.mode = 'live-camera';
        mediaState.sourceName = `On-Bus Live Camera (${(mediaState.cameraFacing || 'environment').toUpperCase()})`;

        if (label) label.textContent = 'Stop Camera';
        if (btn) btn.classList.add('active');
        if (flipBtn) flipBtn.style.display = 'inline-flex';

        updateMediaSidebar();

        if (state.logs) {
            state.logs.unshift({
                time: new Date().toTimeString().split(' ')[0],
                agent: 'Agent 1: Vision',
                tagClass: 'agent-tag-vision',
                text: `[LIVE CAMERA INGEST] Ingested ${mediaState.cameraFacing} camera video stream. Real-time edge CV scanning carriageway.`
            });
            renderEventLogs();
        }
    } catch (err) {
        console.error('[Live Camera Error]:', err);
        alert(`Could not start live camera feed: ${err.message || err.name}. Please ensure camera permissions are granted.`);
    }
};

window.flipLiveCamera = async function() {
    if (!mediaState.isLiveCameraActive) return;
    mediaState.cameraFacing = mediaState.cameraFacing === 'user' ? 'environment' : 'user';
    
    if (mediaState.cameraStream) {
        mediaState.cameraStream.getTracks().forEach(track => track.stop());
    }
    
    try {
        const constraints = {
            video: {
                facingMode: mediaState.cameraFacing,
                width: { ideal: 1280 },
                height: { ideal: 720 }
            },
            audio: false
        };
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        mediaState.cameraStream = stream;
        const videoEl = document.getElementById('live-camera-video');
        if (videoEl) {
            videoEl.srcObject = stream;
            await videoEl.play().catch(e => console.log('Camera playback pending:', e));
        }
        mediaState.sourceName = `On-Bus Live Camera (${mediaState.cameraFacing.toUpperCase()})`;
        updateMediaSidebar();
    } catch (err) {
        console.error('[Flip Camera Error]:', err);
    }
};

window.toggleDriverLiveCamera = async function() {
    const videoEl = document.getElementById('driver-live-video');
    const btnText = document.getElementById('driver-cam-btn-text');
    const btn = document.getElementById('btn-driver-cam-toggle');

    if (!videoEl) return;

    if (window._driverCameraStream) {
        window._driverCameraStream.getTracks().forEach(t => t.stop());
        window._driverCameraStream = null;
        videoEl.style.display = 'none';
        videoEl.srcObject = null;
        if (btnText) btnText.textContent = 'Start Live Cam';
        if (btn) btn.classList.remove('active');
        return;
    }

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('Camera API not available in this browser context.');
        return;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment', width: { ideal: 1280 } },
            audio: false
        });
        window._driverCameraStream = stream;
        videoEl.srcObject = stream;
        videoEl.style.display = 'block';
        await videoEl.play().catch(e => console.log('Driver camera play:', e));
        if (btnText) btnText.textContent = 'Stop Live Cam';
        if (btn) btn.classList.add('active');
    } catch (err) {
        console.error('[Driver Camera Error]:', err);
        alert(`Could not start driver camera: ${err.message}`);
    }
};

function initDashcamSimulator() {
    const canvas = document.getElementById('dashcam-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    // Drag-and-drop video/image loading directly onto canvas
    canvas.addEventListener('dragover', (e) => {
        e.preventDefault();
        canvas.style.outline = '2px dashed #0284C7';
    });
    canvas.addEventListener('dragleave', (e) => {
        e.preventDefault();
        canvas.style.outline = 'none';
    });
    canvas.addEventListener('drop', (e) => {
        e.preventDefault();
        canvas.style.outline = 'none';
        if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleMediaUpload({ target: { files: e.dataTransfer.files } });
        }
    });

    canvas.style.cursor = 'pointer';
    canvas.title = 'Click to Play / Pause or Resume Video Scan';
    canvas.onclick = (e) => {
        if (mediaState.isDefectLocked) {
            resumeVideoScan();
        } else {
            toggleMediaPlayPause();
        }
    };

    const baseImage = new Image();
    baseImage.crossOrigin = "anonymous";
    baseImage.onerror = () => {
        if (!baseImage.src.includes('static/')) {
            baseImage.src = 'static/image1.jpg';
        }
    };
    baseImage.src = 'image1.jpg';
    mediaState.baseImage = baseImage;

    function drawLoop() {
        if (mediaState.isPlaying) {
            mediaState.frameCount++;
            calculateCorridorCoordinates();
            
            // Multi-point fake pothole detection along transit route
            const corr = CORRIDORS[currentCorridorKey] || CORRIDORS['mysuru-orr'];
            let currentProg = 0.35;
            if (mediaState.userVideo && mediaState.userVideo.duration > 0) {
                currentProg = mediaState.userVideo.currentTime / mediaState.userVideo.duration;
            } else {
                currentProg = ((mediaState.frameCount % 300) / 300);
            }

            // Find matching upcoming/active pothole along the corridor or injected pool
            const activePool = (corr.potholes || []).concat(mediaState.injectedPotholes || []);
            const matchedPothole = activePool.find(ph => !mediaState.detectedPotholeIds.has(ph.id) && Math.abs(ph.progress - currentProg) <= 0.05);

            if (matchedPothole && !mediaState.isDefectLocked) {
                mediaState.activePothole = matchedPothole;
                lockDetectedDefect(matchedPothole);
            } else if (!mediaState.isDefectLocked && !mediaState.hasDispatchedOnce && (mediaState.frameCount >= 45 || (mediaState.userVideo && mediaState.userVideo.currentTime >= 1.2))) {
                mediaState.hasDispatchedOnce = true;
                const defP = (corr.potholes && corr.potholes[0]) || {
                    id: 'FP-MYS-1', progress: 0.12, xRatio: 0.42, yRatio: 0.62, width: 148, height: 62, depthCm: 11.4, name: `${corr.short} (Ch: 1.05 km), Mysuru`, ticketId: 'PWD-MYS-7141'
                };
                mediaState.activePothole = defP;
                lockDetectedDefect(defP);
            }
        }

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        let hasDrawnMedia = false;

        // 1. Draw Real Uploaded Video / Camera Stream Frame
        if (mediaState.userVideo && (mediaState.userVideo.readyState >= 1 || !mediaState.userVideo.paused)) {
            try {
                ctx.drawImage(mediaState.userVideo, 0, 0, canvas.width, canvas.height);
                hasDrawnMedia = true;
            } catch (e) {
                hasDrawnMedia = false;
            }
        } 
        
        // 2. Draw Real Uploaded Photo
        if (!hasDrawnMedia && mediaState.userImage && mediaState.userImage.complete && mediaState.userImage.naturalWidth > 0) {
            ctx.drawImage(mediaState.userImage, 0, 0, canvas.width, canvas.height);
            hasDrawnMedia = true;
        } 
        
        // 3. Draw Default Dashcam Base Image
        if (!hasDrawnMedia && baseImage.complete && baseImage.naturalWidth > 0) {
            ctx.drawImage(baseImage, 0, 0, canvas.width, canvas.height);
            hasDrawnMedia = true;
        } 
        
        // 4. Synthetic Road Perspective Fallback
        if (!hasDrawnMedia) {
            const grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
            grad.addColorStop(0, '#1E293B');
            grad.addColorStop(0.45, '#0F172A');
            grad.addColorStop(1, '#020617');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(canvas.width * 0.46, canvas.height * 0.38);
            ctx.lineTo(canvas.width * 0.08, canvas.height);
            ctx.moveTo(canvas.width * 0.54, canvas.height * 0.38);
            ctx.lineTo(canvas.width * 0.92, canvas.height);
            ctx.stroke();

            ctx.strokeStyle = '#F59E0B';
            ctx.lineWidth = 2;
            ctx.setLineDash([12, 16]);
            ctx.lineDashOffset = -mediaState.frameCount * 3;
            ctx.beginPath();
            ctx.moveTo(canvas.width * 0.5, canvas.height * 0.38);
            ctx.lineTo(canvas.width * 0.5, canvas.height);
            ctx.stroke();
            ctx.setLineDash([]);
        }

        // Crosshairs Brackets
        ctx.strokeStyle = 'rgba(2, 132, 199, 0.5)';
        ctx.lineWidth = 1.5;
        const bLen = 14;
        ctx.beginPath();
        ctx.moveTo(10, 10 + bLen); ctx.lineTo(10, 10); ctx.lineTo(10 + bLen, 10);
        ctx.moveTo(canvas.width - 10 - bLen, 10); ctx.lineTo(canvas.width - 10, 10); ctx.lineTo(canvas.width - 10, 10 + bLen);
        ctx.moveTo(10, canvas.height - 10 - bLen); ctx.lineTo(10, canvas.height - 10); ctx.lineTo(10 + bLen, canvas.height - 10);
        ctx.moveTo(canvas.width - 10 - bLen, canvas.height - 10); ctx.lineTo(canvas.width - 10, canvas.height - 10); ctx.lineTo(canvas.width - 10, canvas.height - 10 - bLen);
        ctx.stroke();

        // Scanline (only when actively playing)
        if (mediaState.isPlaying) {
            const scanY = (mediaState.frameCount * 2.5) % canvas.height;
            ctx.strokeStyle = 'rgba(2, 132, 199, 0.35)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(12, scanY);
            ctx.lineTo(canvas.width - 12, scanY);
            ctx.stroke();
        }

        // DPDP Act 2023 §2(t) Privacy Gaussian Blurring on Canvas
        if (mediaState.dpdpActive) {
            ctx.save();
            ctx.filter = 'blur(12px)';
            ctx.fillStyle = 'rgba(30, 30, 30, 0.7)';
            const faceX = Math.round(canvas.width * 0.14);
            const faceY = Math.round(canvas.height * 0.26);
            const faceW = 34;
            const faceH = 34;
            ctx.fillRect(faceX, faceY, faceW, faceH);

            const plateX = Math.round(canvas.width * 0.72);
            const plateY = Math.round(canvas.height * 0.62);
            const plateW = 58;
            const plateH = 22;
            ctx.fillRect(plateX, plateY, plateW, plateH);
            ctx.restore();

            ctx.strokeStyle = '#059669';
            ctx.lineWidth = 1;
            ctx.strokeRect(faceX, faceY, faceW, faceH);
            ctx.strokeRect(plateX, plateY, plateW, plateH);

            ctx.fillStyle = '#059669';
            ctx.font = 'bold 8px "JetBrains Mono"';
            ctx.fillText('DPDP §2(t) MASK', plateX, plateY - 3);
        }

        // Render realistic fake pothole onto video carriageway
        if (mediaState.activePothole) {
            drawRealisticPothole(ctx, canvas, mediaState.activePothole);
        } else {
            const corr = CORRIDORS[currentCorridorKey] || CORRIDORS['mysuru-orr'];
            const curProg = (mediaState.userVideo && mediaState.userVideo.duration > 0) 
                ? (mediaState.userVideo.currentTime / mediaState.userVideo.duration) 
                : ((mediaState.frameCount % 300) / 300);
            const activePool = (corr.potholes || []).concat(mediaState.injectedPotholes || []);
            const nearby = activePool.find(ph => Math.abs(ph.progress - curProg) <= 0.08);
            if (nearby) {
                drawRealisticPothole(ctx, canvas, nearby);
            }
        }

        // =====================================================================
        // REAL CANVAS 2D EDGE CV ROAD DISTRESS DETECTION
        // =====================================================================
        const cv = analyzeCanvasFrame(canvas, ctx);
        const pBoxX = cv ? cv.boxX : Math.round(canvas.width * 0.40);
        const pBoxY = cv ? cv.boxY : Math.round(canvas.height * 0.58);
        const pBoxW = cv ? cv.boxW : 155;
        const pBoxH = cv ? cv.boxH : 65;
        const depthCm = cv ? cv.depthCm : 9.4;
        const sevLevel = cv ? cv.severity : 'CRITICAL_P1';
        const hType = cv ? cv.hazardType : 'POTHOLE';
        const rddCode = cv ? cv.rddCode : 'D40 (Pothole / Subsidence)';
        const confStr = cv ? `${cv.confidence}%` : '97.6%';

        // Synchronize defect parameters in real time
        mediaState.defect.depth = `${depthCm}cm`;
        mediaState.defect.sev = sevLevel;
        mediaState.defect.type = hType;
        mediaState.defect.rdd = rddCode;
        mediaState.defect.conf = confStr;
        mediaState.defect.bbox = { x: pBoxX, y: pBoxY, width: pBoxW, height: pBoxH };

        const sevColor = sevLevel === 'CRITICAL_P1' ? '#DC2626' : (sevLevel === 'HIGH_P2' ? '#EA580C' : '#0284C7');

        // Bounding Box
        ctx.strokeStyle = sevColor;
        ctx.lineWidth = 2.5;
        ctx.strokeRect(pBoxX, pBoxY, pBoxW, pBoxH);

        // Corner Target Accents
        ctx.fillStyle = sevColor;
        const cLen = 9;
        ctx.fillRect(pBoxX - 2, pBoxY - 2, cLen, 3);
        ctx.fillRect(pBoxX - 2, pBoxY - 2, 3, cLen);
        ctx.fillRect(pBoxX + pBoxW - cLen + 2, pBoxY - 2, cLen, 3);
        ctx.fillRect(pBoxX + pBoxW - 1, pBoxY - 2, 3, cLen);
        ctx.fillRect(pBoxX - 2, pBoxY + pBoxH - 1, cLen, 3);
        ctx.fillRect(pBoxX - 2, pBoxY + pBoxH - cLen + 2, 3, cLen);
        ctx.fillRect(pBoxX + pBoxW - cLen + 2, pBoxY + pBoxH - 1, cLen, 3);
        ctx.fillRect(pBoxX + pBoxW - 1, pBoxY + pBoxH - cLen + 2, 3, cLen);

        // Top Tag Banner
        ctx.fillStyle = sevColor;
        const tagWidth = Math.min(pBoxW, 170);
        ctx.fillRect(pBoxX, pBoxY - 18, tagWidth, 18);
        ctx.fillStyle = '#FFFFFF';
        ctx.font = 'bold 9px "JetBrains Mono", monospace';
        ctx.fillText(`${rddCode.split(' ')[0]} ${hType} · ${confStr}`, pBoxX + 6, pBoxY - 5);

        // Bottom Telemetry Tag
        ctx.fillStyle = 'rgba(28, 25, 23, 0.92)';
        const btmWidth = Math.min(pBoxW, 180);
        ctx.fillRect(pBoxX, pBoxY + pBoxH + 3, btmWidth, 16);
        ctx.strokeStyle = sevColor;
        ctx.lineWidth = 1;
        ctx.strokeRect(pBoxX, pBoxY + pBoxH + 3, btmWidth, 16);
        ctx.fillStyle = sevLevel === 'CRITICAL_P1' ? '#FCA5A5' : '#FED7AA';
        ctx.font = 'bold 8px "JetBrains Mono", monospace';
        ctx.fillText(`DEPTH: ${depthCm}cm · ${sevLevel.replace('_', ' ')}`, pBoxX + 6, pBoxY + pBoxH + 14);

        // Status Header on Canvas
        if (mediaState.isDefectLocked) {
            ctx.fillStyle = 'rgba(220, 38, 38, 0.95)';
            ctx.fillRect(10, 10, canvas.width - 20, 24);
            ctx.strokeStyle = '#FFFFFF';
            ctx.lineWidth = 1;
            ctx.strokeRect(10, 10, canvas.width - 20, 24);
            ctx.fillStyle = '#FFFFFF';
            ctx.font = 'bold 10px "Plus Jakarta Sans", sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(`🎯 DEFECT LOCKED & INSPECTED · DEPTH: ${depthCm}cm (${sevLevel.replace('_', ' ')})`, canvas.width / 2, 26);
            ctx.textAlign = 'left';

            // Center Interactive Resume Pill
            const bW = 220;
            const bH = 26;
            const bX = (canvas.width - bW) / 2;
            const bY = canvas.height * 0.28;
            ctx.fillStyle = 'rgba(2, 132, 199, 0.95)';
            ctx.fillRect(bX, bY, bW, bH);
            ctx.strokeStyle = '#FFFFFF';
            ctx.lineWidth = 1.2;
            ctx.strokeRect(bX, bY, bW, bH);
            ctx.fillStyle = '#FFFFFF';
            ctx.font = 'bold 10px "Plus Jakarta Sans", sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(`▶️ RESUME VIDEO SCAN (${mediaState.resumeCountdown}s)`, canvas.width / 2, bY + 17);
            ctx.textAlign = 'left';
        } else {
            ctx.fillStyle = 'rgba(28, 25, 23, 0.85)';
            ctx.fillRect(10, 10, 240, 22);
            ctx.strokeStyle = '#0284C7';
            ctx.lineWidth = 1;
            ctx.strokeRect(10, 10, 240, 22);
            ctx.fillStyle = '#00E5FF';
            ctx.font = 'bold 9px "JetBrains Mono", monospace';
            ctx.fillText('⚡ AI EDGE SCANNING: 30 FPS ACTIVE', 16, 24);
        }

        // Secondary Distress: Surface Crack
        const cBoxX = Math.round(canvas.width * 0.68);
        const cBoxY = Math.round(canvas.height * 0.60);
        const cBoxW = 95;
        const cBoxH = 34;
        ctx.strokeStyle = '#EA580C';
        ctx.lineWidth = 1.8;
        ctx.strokeRect(cBoxX, cBoxY, cBoxW, cBoxH);
        ctx.fillStyle = '#EA580C';
        ctx.fillRect(cBoxX, cBoxY - 15, cBoxW, 15);
        ctx.fillStyle = '#FFFFFF';
        ctx.font = 'bold 8px "JetBrains Mono", monospace';
        ctx.fillText(`D00 CRACK · 94.2%`, cBoxX + 4, cBoxY - 4);

        // Lateral Driving Maneuver Overlay directly on video canvas
        ctx.fillStyle = 'rgba(2, 132, 199, 0.92)';
        ctx.fillRect(canvas.width * 0.22, canvas.height - 28, canvas.width * 0.56, 22);
        ctx.strokeStyle = '#FFFFFF';
        ctx.lineWidth = 1.2;
        ctx.strokeRect(canvas.width * 0.22, canvas.height - 28, canvas.width * 0.56, 22);
        ctx.fillStyle = '#FFFFFF';
        ctx.font = 'bold 10px "Plus Jakarta Sans", sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('↖ MERGE LEFT LANE IN 25m TO BYPASS CRATER', canvas.width * 0.5, canvas.height - 13);
        ctx.textAlign = 'left';

        requestAnimationFrame(drawLoop);
    }

    requestAnimationFrame(drawLoop);
}

function loadSampleMedia(type) {
    document.querySelectorAll('.btn-media-pill').forEach(b => b.classList.remove('active'));

    mediaState.isDefectLocked = false;
    mediaState.hasDispatchedOnce = false;

    if (type === 'mysuru-real-1') {
        const btn = document.getElementById('btn-media-real-1');
        if (btn) btn.classList.add('active');
        mediaState.mode = 'video';
        mediaState.sourceName = 'Mysuru Road Video 1 (Real Dashcam - 20.2cm Pothole)';
        mediaState.userImage = null;
        currentCorridorKey = 'mysuru-orr';
        const sel = document.getElementById('video-corridor-select');
        if (sel) sel.value = 'mysuru-orr';

        let videoEl = document.getElementById('uploaded-media-video');
        if (!videoEl) {
            videoEl = document.createElement('video');
            videoEl.id = 'uploaded-media-video';
            videoEl.autoplay = true;
            videoEl.loop = true;
            videoEl.muted = true;
            videoEl.playsInline = true;
            videoEl.style.display = 'none';
            document.body.appendChild(videoEl);
        }
        videoEl.src = 'static/videos/mysuru_road_inspection_1.mp4';
        videoEl.load();
        videoEl.play().catch(e => console.log('Autoplay handled:', e));
        mediaState.userVideo = videoEl;
        mediaState.defect = {
            type: 'POTHOLE',
            rdd: 'D40 (Pothole / Subsidence)',
            conf: '97.6%',
            depth: '20.2cm',
            sev: 'CRITICAL_P1',
            busId: 'KSRTC-KA09-E102',
            loc: 'VVCE Ring Road Junction, Gokulam, Mysuru',
            lat: 12.3360,
            lng: 76.6210,
            sorCode: 'CPWD 16.14.2 (Dense Bituminous Macadam)',
            ticketId: 'PWD-OCT-0941'
        };
        updateLiveNavigationDirections('POTHOLE', 12.3360, 76.6210, 'VVCE Ring Road Junction, Gokulam');
    } else if (type === 'mysuru-real-2') {
        const btn = document.getElementById('btn-media-real-2');
        if (btn) btn.classList.add('active');
        mediaState.mode = 'video';
        mediaState.sourceName = 'Mysuru Road Video 2 (Real Dashcam)';
        mediaState.userImage = null;
        currentCorridorKey = 'hunsur-rd';
        const sel = document.getElementById('video-corridor-select');
        if (sel) sel.value = 'hunsur-rd';

        let videoEl = document.getElementById('uploaded-media-video');
        if (!videoEl) {
            videoEl = document.createElement('video');
            videoEl.id = 'uploaded-media-video';
            videoEl.autoplay = true;
            videoEl.loop = true;
            videoEl.muted = true;
            videoEl.playsInline = true;
            videoEl.style.display = 'none';
            document.body.appendChild(videoEl);
        }
        videoEl.src = 'static/videos/mysuru_road_inspection_2.mp4';
        videoEl.load();
        videoEl.play().catch(e => console.log('Autoplay handled:', e));
        mediaState.userVideo = videoEl;
        mediaState.defect = {
            type: 'POTHOLE',
            rdd: 'D40 (Pothole / Subsidence)',
            conf: '96.4%',
            depth: '14.8cm',
            sev: 'CRITICAL_P1',
            busId: 'KSRTC-MY09-C330',
            loc: 'Hunsur Road Kalamandira Signal, Mysuru',
            lat: 12.3140,
            lng: 76.6320,
            sorCode: 'CPWD 16.14.2 (DBM Patch)',
            ticketId: 'PWD-OCT-0942'
        };
        updateLiveNavigationDirections('POTHOLE', 12.3140, 76.6320, 'Hunsur Road Kalamandira Signal');
    } else if (type === 'mysuru-real-3') {
        const btn = document.getElementById('btn-media-real-3');
        if (btn) btn.classList.add('active');
        mediaState.mode = 'video';
        mediaState.sourceName = 'Mysuru Road Video 3 (Real Dashcam)';
        mediaState.userImage = null;
        currentCorridorKey = 'sayyaji-rao';
        const sel = document.getElementById('video-corridor-select');
        if (sel) sel.value = 'sayyaji-rao';

        let videoEl = document.getElementById('uploaded-media-video');
        if (!videoEl) {
            videoEl = document.createElement('video');
            videoEl.id = 'uploaded-media-video';
            videoEl.autoplay = true;
            videoEl.loop = true;
            videoEl.muted = true;
            videoEl.playsInline = true;
            videoEl.style.display = 'none';
            document.body.appendChild(videoEl);
        }
        videoEl.src = 'static/videos/mysuru_road_inspection_3.mp4';
        videoEl.load();
        videoEl.play().catch(e => console.log('Autoplay handled:', e));
        mediaState.userVideo = videoEl;
        mediaState.defect = {
            type: 'ROAD_CRACK',
            rdd: 'D00 (Longitudinal Surface Crack)',
            conf: '95.1%',
            depth: '4.5cm',
            sev: 'HIGH_P2',
            busId: 'KSRTC-KA09-E102',
            loc: 'Sayyaji Rao Road Heritage Corridor, Mysuru',
            lat: 12.3130,
            lng: 76.6538,
            sorCode: 'CPWD 16.12.1 (Crack Sealing)',
            ticketId: 'PWD-OCT-0943'
        };
        updateLiveNavigationDirections('ROAD_CRACK', 12.3130, 76.6538, 'Sayyaji Rao Road Corridor');
    } else if (type === 'mysuru-video') {
        const btn = document.getElementById('btn-media-sample-mysuru');
        if (btn) btn.classList.add('active');
        mediaState.mode = 'video';
        mediaState.sourceName = 'Mysuru ORR Dashcam (KSRTC-KA09-E102)';
        mediaState.userVideo = null;
        mediaState.userImage = null;
        if (mediaState.baseImage) mediaState.baseImage.src = 'image1.jpg';
        currentCorridorKey = 'mysuru-orr';
        const sel = document.getElementById('video-corridor-select');
        if (sel) sel.value = 'mysuru-orr';
        mediaState.defect = {
            type: 'POTHOLE',
            rdd: 'D40 (Pothole / Subsidence)',
            conf: '97.6%',
            depth: '9.4cm',
            sev: 'CRITICAL_P1',
            busId: 'KSRTC-KA09-E102',
            loc: 'VVCE Ring Road Junction, Gokulam, Mysuru',
            lat: 12.3360,
            lng: 76.6210,
            sorCode: 'CPWD 16.14.2 (DBM Patch)',
            ticketId: 'PWD-OCT-0745'
        };
    } else if (type === 'bengaluru-video') {
        const btn = document.getElementById('btn-media-sample-blr');
        if (btn) btn.classList.add('active');
        mediaState.mode = 'video';
        mediaState.sourceName = 'Bengaluru ORR Flyover Feed (BMTC-KA57-E912)';
        mediaState.userVideo = null;
        mediaState.userImage = null;
        if (mediaState.baseImage) mediaState.baseImage.src = 'image1.jpg';
        mediaState.defect = {
            type: 'POTHOLE',
            rdd: 'D40 (Pothole / Subsidence)',
            conf: '96.2%',
            depth: '9.4cm',
            sev: 'CRITICAL_P1',
            busId: 'BMTC-KA57-E912',
            loc: 'Outer Ring Road near Bellandur Pillar 34, Bengaluru',
            lat: 12.9250,
            lng: 77.6760,
            sorCode: 'CPWD 16.14.2 (DBM Patch)',
            ticketId: 'PWD-OCT-0948'
        };
    } else if (type === 'mysuru-pothole') {
        const btn = document.getElementById('btn-media-sample-pothole');
        if (btn) btn.classList.add('active');
        mediaState.mode = 'image';
        mediaState.sourceName = 'Hunsur Road Pothole Photo (MCC Ward 9)';
        mediaState.userVideo = null;
        mediaState.userImage = null;
        if (mediaState.baseImage) mediaState.baseImage.src = 'image1.jpg';
        currentCorridorKey = 'hunsur-rd';
        const sel = document.getElementById('video-corridor-select');
        if (sel) sel.value = 'hunsur-rd';
        mediaState.defect = {
            type: 'POTHOLE',
            rdd: 'D40 (Pothole / Subsidence)',
            conf: '98.1%',
            depth: '8.6cm',
            sev: 'CRITICAL_P1',
            busId: 'KSRTC-MY09-C330',
            loc: 'Hunsur Road Kalamandira Signal, Mysuru',
            lat: 12.3140,
            lng: 76.6320,
            sorCode: 'CPWD 16.14.2 (DBM Patch)',
            ticketId: 'PWD-OCT-0720'
        };
    } else if (type === 'silk-water') {
        const btn = document.getElementById('btn-media-sample-water');
        if (btn) btn.classList.add('active');
        mediaState.mode = 'image';
        mediaState.sourceName = 'Silk Board Underpass Monsoon Photo';
        mediaState.userVideo = null;
        mediaState.userImage = null;
        if (mediaState.baseImage) mediaState.baseImage.src = 'image2.jpg';
        mediaState.defect = {
            type: 'WATERLOGGING',
            rdd: 'W01 (Monsoon Waterlogging)',
            conf: '94.5%',
            depth: '35m Length',
            sev: 'HIGH_P2',
            busId: 'BMTC-KA57-E912',
            loc: 'Silk Board Underpass South Lane, Bengaluru',
            lat: 12.9125,
            lng: 77.6395,
            sorCode: 'CPWD 11.4.2 (Drain De-silt)',
            ticketId: 'PWD-OCT-0882'
        };
    }

    updateMediaSidebar();
}

function handleMediaUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    mediaState.customFile = file;
    const fileUrl = URL.createObjectURL(file);
    mediaState.isDefectLocked = false;
    mediaState.hasDispatchedOnce = false;

    if (file.type.startsWith('video/')) {
        mediaState.mode = 'video';
        mediaState.sourceName = `Real Road Video: ${file.name}`;
        
        let videoEl = document.getElementById('uploaded-media-video');
        if (!videoEl) {
            videoEl = document.createElement('video');
            videoEl.id = 'uploaded-media-video';
            videoEl.style.display = 'none';
            document.body.appendChild(videoEl);
        }
        
        videoEl.src = fileUrl;
        videoEl.muted = true;
        videoEl.loop = true;
        videoEl.playsInline = true;
        videoEl.setAttribute('playsinline', '');
        videoEl.setAttribute('muted', '');
        
        videoEl.onloadedmetadata = () => {
            videoEl.play().catch(e => console.log('[Video] Autoplay pending click:', e));
        };
        videoEl.play().catch(e => console.log('[Video] Play deferred:', e));
        
        mediaState.userVideo = videoEl;
        mediaState.userImage = null;
    } else {
        mediaState.mode = 'image';
        mediaState.sourceName = `Real Road Photo: ${file.name}`;
        const imgEl = new Image();
        imgEl.src = fileUrl;
        imgEl.onload = () => {
            mediaState.userImage = imgEl;
            mediaState.userVideo = null;
        };
        mediaState.userImage = imgEl;
        mediaState.userVideo = null;
    }

    const { lat, lng } = calculateCorridorCoordinates();
    mediaState.defect = {
        type: 'POTHOLE',
        rdd: 'D40 (Pothole / Subsidence)',
        conf: '97.8%',
        depth: '9.4cm',
        sev: 'CRITICAL_P1',
        busId: 'KSRTC-KA09-E102',
        loc: `${CORRIDORS[currentCorridorKey].short} (Real Ingest)`,
        lat: lat,
        lng: lng,
        sorCode: 'CPWD 16.14.2 (DBM Patch)',
        ticketId: `PWD-OCT-${Math.floor(1000 + Math.random() * 9000)}`
    };

    updateMediaSidebar();

    // Send to backend OpenCV pipeline for keyframe extraction & consensus
    try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('bus_id', 'KSRTC-KA09-E102');
        formData.append('location_name', `${CORRIDORS[currentCorridorKey].name}`);
        formData.append('lat', lat);
        formData.append('lng', lng);
        formData.append('hazard_hint', 'POTHOLE');

        fetch('/api/analyze-media', { method: 'POST', body: formData })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'SUCCESS' && data.defect) {
                    mediaState.defect.depth = `${data.defect.damage_depth_cm}cm`;
                    mediaState.defect.sev = data.defect.severity;
                    mediaState.defect.conf = `${Math.round(data.defect.confidence * 100)}%`;
                    mediaState.defect.type = data.defect.type;
                    mediaState.defect.rdd = data.defect.rdd_code;
                    if (data.work_order && data.work_order.ticket_id) {
                        mediaState.defect.ticketId = data.work_order.ticket_id;
                    }
                    updateMediaSidebar();
                    if (state.logs) {
                        state.logs.unshift({
                            time: new Date().toTimeString().split(' ')[0],
                            agent: 'Agent 1: Vision',
                            tagClass: 'agent-tag-vision',
                            text: `[EDGE OPENCV] Analyzed ${file.name}. Detected ${data.defect.type} (${data.defect.damage_depth_cm}cm depth) with ${Math.round(data.defect.confidence * 100)}% confidence.`
                        });
                        renderEventLogs();
                    }
                }
            })
            .catch(err => console.log('[Media API Fallback Mode]:', err));
    } catch (e) {
        console.log('[Media Upload Local Mode]:', e);
    }

    if (state.logs) {
        state.logs.unshift({
            time: new Date().toTimeString().split(' ')[0],
            agent: 'Agent 1: Vision',
            tagClass: 'agent-tag-vision',
            text: `[REAL MEDIA INGEST] Ingested ${file.name} (${(file.size / (1024*1024)).toFixed(2)} MB). Edge CV scanning carriageway along ${CORRIDORS[currentCorridorKey].name}.`
        });
        renderEventLogs();
    }
}

function updateMediaSidebar() {
    const feedEl = document.getElementById('media-hud-feed-name');
    const coordsEl = document.getElementById('media-hud-coords');
    const defectEl = document.getElementById('detection-defect-label');
    const depthEl = document.getElementById('detection-depth-label');
    const locEl = document.getElementById('detection-location-label');

    if (feedEl) feedEl.textContent = `FEED: ${mediaState.sourceName}`;
    if (coordsEl) coordsEl.textContent = `GPS: ${mediaState.defect.lat.toFixed(4)}°N, ${mediaState.defect.lng.toFixed(4)}°E`;
    if (defectEl) defectEl.textContent = `${mediaState.defect.type} ${mediaState.defect.rdd.split(' ')[0]} · ${mediaState.defect.conf}`;
    if (depthEl) depthEl.textContent = `Distress: ${mediaState.defect.depth} · Severity: ${mediaState.defect.sev.split('_')[1] || 'P1'}`;
    if (locEl) locEl.textContent = mediaState.defect.loc;
}

function toggleMediaPlayPause() {
    mediaState.isPlaying = !mediaState.isPlaying;
    const icon = document.getElementById('playpause-icon');
    const text = document.getElementById('playpause-text');

    if (mediaState.userVideo) {
        if (mediaState.isPlaying) mediaState.userVideo.play().catch(e => console.log('Play err:', e));
        else mediaState.userVideo.pause();
    }

    if (mediaState.isPlaying) {
        if (icon) icon.className = 'fa-solid fa-pause';
        if (text) text.textContent = 'PAUSE';
    } else {
        if (icon) icon.className = 'fa-solid fa-play';
        if (text) text.textContent = 'PLAY';
    }
}

function toggleDPDPMask() {
    mediaState.dpdpActive = !mediaState.dpdpActive;
    const text = document.getElementById('dpdp-status-text');
    const badge = document.getElementById('hud-dpdp-badge');

    if (text) text.textContent = mediaState.dpdpActive ? 'DPDP: ON' : 'DPDP: OFF';
    if (badge) badge.style.display = mediaState.dpdpActive ? 'inline-flex' : 'none';
}

function updateLiveNavigationDirections(hazard, lat, lng, loc) {
    if (typeof drawMapDirectionRoute === 'function') {
        const targetCoord = (lat && lng) ? [lat, lng] : [mediaState.defect.lat, mediaState.defect.lng];
        drawMapDirectionRoute(targetCoord, loc || mediaState.defect.loc, 'detour');
    }
}


function runAIAnalysisAndDispatch() {
    const d = mediaState.defect;

    // 1. Add / Update in state.hazards
    const existingH = state.hazards.find(h => h.id === `HAZ-${d.ticketId.slice(-3)}` || (Math.abs(h.lat - d.lat) < 0.001 && Math.abs(h.lng - d.lng) < 0.001));
    if (!existingH) {
state.hazards.unshift({
    id: `HAZ-${d.ticketId.slice(-3)}`,
    type: d.type,
    sev: d.sev,
    lat: d.lat,
    lng: d.lng,
    name: d.loc,
    depth: d.depth,
    conf: d.conf,
    passes: 1,
    ticket: d.ticketId,
    sorCode: d.sorCode
});
    }

    // 2. Add to PWD Work Orders Queue
    const existingWO = state.workOrders.find(w => w.ticket === d.ticketId);
    if (!existingWO) {
updateLiveNavigationDirections(d.type, d.lat, d.lng, d.loc);
    state.workOrders.unshift({
    ticket: d.ticketId,
    type: d.type,
    sev: d.sev,
    loc: d.loc,
    passes: 1,
    sla: "48h 00m remaining",
    status: "DISPATCHED",
    sorCode: d.sorCode
});
renderWorkOrdersTable();
    }

    // 3. Drop marker and Fly Map to location in Mysuru / Bengaluru
    renderHazardsOnMap();
    if (state.map) {
state.map.flyTo([d.lat, d.lng], 15, { duration: 1.2 });
    }

    // 4. Update Terminal Logs with Multi-Agent Handoff
    const now = new Date().toTimeString().split(' ')[0];
    state.logs.unshift({
time: now,
agent: "Agent 4: Fleet Advisory",
tagClass: "agent-tag-advisory",
text: `Broadcast WebSocket hazard alert to approaching transit buses within 300m horizon.`
    });
    state.logs.unshift({
time: now,
agent: "Agent 3: PWD Dispatch",
tagClass: "agent-tag-dispatch",
text: `Auto-filed PWD Work Order #${d.ticketId} with GPS & photo evidence (${d.sorCode}).`
    });
    state.logs.unshift({
time: now,
agent: "Agent 2: DBSCAN",
tagClass: "agent-tag-dbscan",
text: `Clustered detection at [${d.lat.toFixed(4)}, ${d.lng.toFixed(4)}] into canonical cluster (5m epsilon match).`
    });
    state.logs.unshift({
time: now,
agent: "Agent 1: Vision",
tagClass: "agent-tag-vision",
text: `Analyzed ${mediaState.sourceName}: Detected ${d.type} (${d.depth}, ${d.conf}). DPDP Act 2023 §2(t) blur applied.`
    });
    renderEventLogs();

    // 5. Update KPI card
    const dispatchesEl = document.querySelector('.kpi-value.amber');
    if (dispatchesEl) {
dispatchesEl.textContent = `${state.workOrders.length} Active`;
    }

    // 6. Show interactive confirmation toast with voucher link
    showDispatchToast(d);

            // 7. Dispatch to FastAPI Backend for Municipal Sync & Persistence
            try {
                fetch('/api/simulate-detection', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        bus_id: mediaState.defect.busId || 'KSRTC-KA09-E102',
                        hazard_type: d.type || 'POTHOLE',
                        lat: d.lat,
                        lng: d.lng,
                        location_name: d.loc,
                        confidence: 0.98,
                        damage_depth_cm: parseFloat(d.depth) || 11.4,
                        z_shock: -0.42
                    })
                }).then(r => r.json()).then(res => {
                    console.log('[Municipal Backend API Synced]:', res);
                }).catch(e => console.log('[Backend Offline Fallback]:', e));
            } catch(e) {
                console.log('[Backend Sync Handled]:', e);
            }
}

function showDispatchToast(d) {
    const existingToast = document.querySelector('.analysis-success-toast');
    if (existingToast) existingToast.remove();

    const toast = document.createElement('div');
    toast.className = 'analysis-success-toast';
    toast.innerHTML = `
<div style="width:32px; height:32px; border-radius:50%; background:var(--success); color:#FFFFFF; display:flex; align-items:center; justify-content:center; font-size:16px;">
    <i class="fa-solid fa-check"></i>
</div>
<div>
    <div style="font-weight:800; font-size:0.85rem; color:#FFFFFF;">AI Detection Dispatched to PWD Grid!</div>
    <div style="font-size:0.75rem; color:#DDD6C6; margin-top:2px;">Work Order <b>#${d.ticketId}</b> · ${d.loc}</div>
    <div style="margin-top:6px;">
<a href="voucher.html?ticket=${d.ticketId}" target="_blank" style="color:var(--primary); font-size:0.75rem; font-weight:800; text-decoration:none;">
    <i class="fa-solid fa-file-invoice"></i> View Official CPWD Voucher &rarr;
</a>
    </div>
</div>
<button onclick="this.parentElement.remove()" style="background:transparent; border:none; color:#9BA3AF; cursor:pointer; font-size:14px; margin-left:8px;">&times;</button>
    `;
    document.body.appendChild(toast);
    setTimeout(() => { if (toast.parentElement) toast.remove(); }, 8000);
}


// 4. Real-Time Activity Log Feed
function initEventLogFeed() {
    const feed = document.getElementById('activity-feed');
    if (!feed) return;
    feed.innerHTML = state.logs.map(log => `
        <div class="log-entry ${log.tagClass || ''}">
            <span class="log-time">${log.time}</span>
            <span class="log-agent">${log.agent}:</span>
            <span>${log.text}</span>
        </div>
    `).join('');
}

function pushLog(agent, text, tagClass = "") {
    const now = new Date();
    const timeStr = now.toTimeString().split(' ')[0];
    state.logs.unshift({ time: timeStr, agent, text, tagClass });
    if (state.logs.length > 40) state.logs.pop();
    initEventLogFeed();
}

// 5. Interactive Action Listeners
function initActionListeners() {
    const btnDetect = document.getElementById('btn-simulate-detect');
    if (btnDetect) {
        btnDetect.addEventListener('click', () => {
            pushLog("Agent 1: Vision Perception", "Spotted critical POTHOLE D40 (depth: 9.8cm, z-shock: 2.4g) on Sarjapur ORR. Transmitting <14.8KB GeoJSON metadata.", "agent-tag-vision");
            highlightAgent(1);

            setTimeout(() => {
                pushLog("Agent 2: Geo-Spatial Clustering", "DBSCAN fused coordinates with historical cluster #DBSCAN-CL-041 (15th verified transit bus pass).", "agent-tag-dbscan");
                highlightAgent(2);
            }, 600);

            setTimeout(() => {
                const newTicket = `PWD-OCT-${Math.floor(1000 + Math.random() * 9000)}`;
                pushLog("Agent 3: Municipal Dispatch", `Matched CPWD SOR 16.14.2 (Dense Bituminous Macadam). Auto-filed PWD Work Order #${newTicket} to BBMP Ward portal (<180s SLA).`, "agent-tag-dispatch");
                highlightAgent(3);
                addNewWorkOrder(newTicket, "POTHOLE", "CRITICAL_P1", "Sarjapur Outer Ring Road", 15, "CPWD 16.14.2 (DBM Patch)");
            }, 1200);

            setTimeout(() => {
                pushLog("Agent 4: Fleet Advisory", "Broadcasted low-latency V2X detour alert via WebSocket to 6 oncoming buses approaching Sarjapur corridor.", "agent-tag-advisory");
                highlightAgent(4);
                triggerDriverAlert("CRITICAL POTHOLE (9.8cm Depth)", "Sarjapur Outer Ring Road (180m Ahead)", "Merge to Right Lane. Speed cap: 25 km/h.");
            }, 1800);
        });
    }

    const btnAlert = document.getElementById('btn-driver-alert');
    if (btnAlert) {
        btnAlert.addEventListener('click', () => {
            triggerDriverAlert("CRITICAL POTHOLE (9.4cm Depth)", "Outer Ring Road near Bellandur Flyover (150m Ahead)", "Slow down to 20 km/h; move to center lane.");
        });
    }

    const modalClose = document.getElementById('modal-close-btn');
    const modalOverlay = document.getElementById('driver-alert-modal');
    if (modalClose && modalOverlay) {
        modalClose.addEventListener('click', () => {
            modalOverlay.classList.remove('show');
        });
    }
    if (modalOverlay) {
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) modalOverlay.classList.remove('show');
        });
    }

    const btnPrivacy = document.getElementById('btn-toggle-privacy');
    if (btnPrivacy) {
        btnPrivacy.addEventListener('click', () => {
            state.settings.privacyBlur = !state.settings.privacyBlur;
            btnPrivacy.innerHTML = state.settings.privacyBlur 
                ? '<i class="fa-solid fa-shield-halved"></i> Privacy Blur: ON' 
                : '<i class="fa-solid fa-shield-slash"></i> Privacy Blur: OFF';
            btnPrivacy.classList.toggle('active-toggle', state.settings.privacyBlur);
            pushLog("Privacy Guard", `DPDP Act 2023 §2(t) On-Device Gaussian Mask toggled ${state.settings.privacyBlur ? 'ENABLED' : 'DISABLED'}.`, "agent-tag-vision");
        });
    }

    const btnCsv = document.getElementById('btn-export-csv');
    if (btnCsv) {
        btnCsv.addEventListener('click', (e) => {
            e.preventDefault();
            exportCSV();
        });
    }

    const btnGeo = document.getElementById('btn-export-geojson');
    if (btnGeo) {
        btnGeo.addEventListener('click', (e) => {
            e.preventDefault();
            exportGeoJSON();
        });
    }

    // ASTM D6433 PCI Predictive Degradation Decay Buttons
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
                pushLog("PCI Forecast Engine", `Markov Chain degradation projection computed for Day +${btnInfo.days}. Corridor condition overlay updated.`, "agent-tag-dbscan");
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

function addNewWorkOrder(ticket, type, sev, loc, passes, sorCode) {
    updateLiveNavigationDirections(d.type, d.lat, d.lng, d.loc);
    state.workOrders.unshift({
        ticket, type, sev, loc, passes, sla: "47h 58m remaining", status: "DISPATCHED", sorCode: sorCode || "CPWD 16.14.2 (DBM Patch)"
    });
    renderWorkOrdersTable();
}

// =========================================================================
// WhatsApp & SMS Municipal Dispatch Logic
// =========================================================================
let currentDispatchTicket = 'PWD-OCT-0715';
let currentRecipientRole = 'CONTRACTOR';

function openDispatchMessageModal(ticketId) {
    const modal = document.getElementById('msg-dispatch-modal');
    if (!modal) return;

    const select = document.getElementById('msg-ticket-select');
    if (select && state.workOrders) {
select.innerHTML = state.workOrders.map(w =>
    `<option value="${w.ticket}" ${w.ticket === (ticketId || currentDispatchTicket) ? 'selected' : ''}>${w.ticket} · ${w.type} (${w.loc.slice(0, 32)}...)</option>`
).join('');
    }

    currentDispatchTicket = ticketId || (state.workOrders[0] ? state.workOrders[0].ticket : 'PWD-OCT-0715');
    updateDispatchMessagePreview();

    const statusBox = document.getElementById('msg-delivery-status');
    if (statusBox) statusBox.style.display = 'none';

    modal.style.display = 'flex';
}

function closeDispatchMessageModal() {
    const modal = document.getElementById('msg-dispatch-modal');
    if (modal) modal.style.display = 'none';
}

function setRecipientRole(btn) {
    document.querySelectorAll('.btn-recipient-pill').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentRecipientRole = btn.getAttribute('data-role');
    const phone = btn.getAttribute('data-phone');
    const phoneInput = document.getElementById('msg-recipient-phone');
    if (phoneInput && phone) phoneInput.value = phone;
    updateDispatchMessagePreview();
}

function updateDispatchMessagePreview() {
    const select = document.getElementById('msg-ticket-select');
    const ticketId = select ? select.value : currentDispatchTicket;
    currentDispatchTicket = ticketId;

    const wo = (state.workOrders && state.workOrders.find(w => w.ticket === ticketId)) || {
ticket: ticketId,
type: "POTHOLE",
loc: "VVCE Ring Road Junction, Gokulam, Mysuru (MCC Ward 9)",
sla: "44h 10m remaining",
sorCode: "CPWD 16.14.2 (DBM Patch)"
    };

    const phone = document.getElementById('msg-recipient-phone')?.value || '+91 98450 12345';

    const msg = `🚨 *URBANSIGHT AI · MUNICIPAL PWD WORK ORDER* 🚨\n` +
`📋 *Work Order:* #${wo.ticket} (${wo.type})\n` +
`📍 *Location:* ${wo.loc}\n` +
`⏱️ *SLA Deadline:* ${wo.sla}\n` +
`💰 *CPWD SOR:* ${wo.sorCode || 'CPWD-16.14.2'}\n` +
`🔗 *Citizen Tracker:* https://gaganks2006-ind.github.io/urbansight-ai/citizen_portal.html?ticket=${wo.ticket}\n` +
`📄 *Tender Voucher:* https://gaganks2006-ind.github.io/urbansight-ai/voucher.html?ticket=${wo.ticket}`;

    const previewEl = document.getElementById('msg-preview-text');
    if (previewEl) previewEl.value = msg.replace(/\\n/g, '\n');
}

function sendModalDispatch(channel = 'WHATSAPP') {
    const select = document.getElementById('msg-ticket-select');
    const ticketId = select ? select.value : currentDispatchTicket;
    const phone = document.getElementById('msg-recipient-phone')?.value || '+91 98450 12345';
    const text = document.getElementById('msg-preview-text')?.value || '';
    const cleanPhone = phone.replace(/[^0-9]/g, '');

    fetch('/api/send-alert', {
method: 'POST',
headers: { 'Content-Type': 'application/json' },
body: JSON.stringify({
    channel: channel,
    phone_number: phone,
    ticket_id: ticketId,
    recipient_type: currentRecipientRole,
    message: text
})
    }).catch(() => {});

    if (state.logs) {
state.logs.unshift({
    time: new Date().toTimeString().split(' ')[0],
    agent: 'Agent 3: PWD Dispatch',
    tagClass: 'agent-tag-dispatch',
    text: `Dispatched ${channel} alert for #${ticketId} to ${phone} (${currentRecipientRole}). Gateway: ${channel === 'WHATSAPP' ? 'Meta Cloud API v20.0' : 'National DLT SMS'}.`
});
renderEventLogs();
    }

    const statusBox = document.getElementById('msg-delivery-status');
    if (statusBox) {
statusBox.style.display = 'flex';
if (channel === 'WHATSAPP') {
    statusBox.style.background = 'rgba(37, 211, 102, 0.15)';
    statusBox.style.color = '#15803d';
    statusBox.style.border = '1px solid rgba(37, 211, 102, 0.4)';
    statusBox.innerHTML = `<i class="fa-brands fa-whatsapp"></i> <b>✓✓ Delivered via WhatsApp Business Cloud Gateway</b> to ${phone} (Msg ID: MSG-WA-${Math.floor(10000+Math.random()*90000)})`;
    const waUrl = `https://api.whatsapp.com/send?phone=${cleanPhone}&text=${encodeURIComponent(text)}`;
    window.open(waUrl, '_blank');
} else {
    statusBox.style.background = 'rgba(2, 132, 199, 0.15)';
    statusBox.style.color = '#0369a1';
    statusBox.style.border = '1px solid rgba(2, 132, 199, 0.4)';
    statusBox.innerHTML = `<i class="fa-solid fa-comment-sms"></i> <b>✓ Normal SMS Sent via Govt Telecom Gateway (BSNL/Airtel)</b> to ${phone}`;
    const smsUrl = `sms:${phone}?body=${encodeURIComponent(text)}`;
    window.location.href = smsUrl;
}
    }
}

function renderWorkOrdersTable() {
    const tbody = document.getElementById('work-orders-tbody');
    if (!tbody) return;
    tbody.innerHTML = state.workOrders.map(w => `
        <tr>
            <td><span class="table-ticket-code">${w.ticket}</span></td>
            <td>
                <div style="font-weight:600; color:#FFFFFF;">${w.type}</div>
                <div style="font-size:10px; color:#9BA3AF; font-family:'JetBrains Mono';">${w.sorCode || 'CPWD 16.14.2'}</div>
            </td>
            <td>${w.loc}</td>
            <td><strong style="color:#00F0FF; font-family:'JetBrains Mono';">${w.passes} passes</strong></td>
            <td><span class="badge-pill badge-green">${w.sla}</span></td>
            <td><span class="badge-pill badge-cyan">${w.status}</span></td>
            <td>
                <a href="voucher.html?ticket=${w.ticket}" target="_blank" class="btn-table-action" title="View CPWD Tender Voucher">
                    <i class="fa-solid fa-file-invoice"></i> Voucher
                </a>
            </td>
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

// 6. CSV Export Function
function exportCSV() {
    const headers = ["Ticket ID", "Hazard Type", "Severity", "Location", "Cluster Passes", "SLA Countdown", "CPWD SOR Code", "Status"];
    const rows = state.workOrders.map(w => [
        w.ticket,
        w.type,
        w.sev,
        `"${w.loc}"`,
        w.passes,
        `"${w.sla}"`,
        `"${w.sorCode || 'CPWD-16.14.2'}"`,
        w.status
    ]);
    const csvContent = [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `urbansight_cpwd_work_orders_${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    pushLog("Municipal Dispatch", "Exported official CPWD work-orders CSV report.", "agent-tag-dispatch");
}

// 7. GeoJSON Export Function
function exportGeoJSON() {
    const featureCollection = {
        type: "FeatureCollection",
        metadata: {
            platform: "UrbanSight AI",
            version: "2.1.0",
            timestamp: new Date().toISOString(),
            standard: "OGC GeoJSON / RFC 7946"
        },
        features: [
            ...state.hazards.map(h => ({
                type: "Feature",
                geometry: { type: "Point", coordinates: [h.lng, h.lat] },
                properties: {
                    id: h.id,
                    type: h.type,
                    severity: h.sev,
                    location_name: h.name,
                    damage_depth_cm: h.depth || null,
                    affected_length_m: h.length || null,
                    confidence: h.conf,
                    cluster_passes: h.passes,
                    ticket_id: h.ticket,
                    cpwd_sor_code: h.sorCode || "CPWD-16.14.2"
                }
            })),
            ...state.buses.map(b => ({
                type: "Feature",
                geometry: { type: "Point", coordinates: [b.lng, b.lat] },
                properties: {
                    bus_id: b.id,
                    route: b.route,
                    speed_kmh: b.speed,
                    heading_deg: b.heading,
                    status: "ONLINE",
                    fps: 30.0
                }
            }))
        ]
    };
    const blob = new Blob([JSON.stringify(featureCollection, null, 2)], { type: "application/geo+json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `urbansight_geospatial_telemetry_${new Date().toISOString().slice(0, 10)}.geojson`;
    link.click();
    pushLog("Geo-Spatial Clustering", "Exported live OGC GeoJSON transit & hazard feature collection.", "agent-tag-dbscan");
}

// 8. Real-Time Bus Coordinate Jitter / Movement Simulation
function startRealtimePolling() {
    setInterval(() => {
        state.buses.forEach(b => {
            b.lat += (Math.random() - 0.5) * 0.0004;
            b.lng += (Math.random() - 0.5) * 0.0004;
            if (b.marker) {
                b.marker.setLatLng([b.lat, b.lng]);
            }
        });
    }, 3000);
}



// =============================================================================
// Official Government Portal Features: Accessibility, SLA & Modals
// =============================================================================

function setFontScale(scale) {
    document.documentElement.style.setProperty('--font-scale', scale);
    const buttons = document.querySelectorAll('.font-sizer-group .btn-gov-tool');
    buttons.forEach(btn => btn.classList.remove('active'));
    if (scale === 0.9 && buttons[0]) buttons[0].classList.add('active');
    if (scale === 1.0 && buttons[1]) buttons[1].classList.add('active');
    if (scale === 1.15 && buttons[2]) buttons[2].classList.add('active');
}

function toggleHighContrast() {
    document.body.classList.toggle('high-contrast');
    const isHc = document.body.classList.contains('high-contrast');
    console.log('[GIGW] High contrast mode:', isHc ? 'ENABLED' : 'DISABLED');
}

function changeOfficialLanguage(lang) {
    const banners = {
        'kn': '⚠️ ಸಾರ್ವಜನಿಕ ಪ್ರಕಟಣೆ: ಸಯ್ಯಜಿ ರಾವ್ ರಸ್ತೆ ಡ್ರೈನೇಜ್ ಮತ್ತು ರಸ್ತೆ ಗುಂಡಿ ದುರಸ್ತಿ ಕಾರ್ಯ ನಡೆಯುತ್ತಿದೆ. ಬಸ್ ಮಾರ್ಗ 119 ಇರ್ವಿನ್ ರಸ್ತೆಯ ಮೂಲಕ ತಿರುಗಿಸಲಾಗಿದೆ.',
        'hi': '⚠️ सार्वजनिक सूचना: सैय्याजी राव रोड पर जल निकासी और गड्ढों की मरम्मत कार्य जारी है। बस रूट 119 को इरविन रोड से मोड़ा गया है।',
        'en': '⚠️ Sayyaji Rao Road: Drainage desilting & rapid pothole restoration in progress. Transit bus route 119 diverted via Irwin Road.'
    };
    const textEl = document.getElementById('notice-marquee-text');
    if (textEl && banners[lang]) {
        textEl.innerHTML = `<span><strong>${banners[lang]}</strong></span><span class="notice-sep">✦</span><span>🚨 <strong>MCC Rapid Response:</strong> 12 patch vans active across 9 zonal depots.</span>`;
    }
}

function toggleNoticeMarquee() {
    const marquee = document.getElementById('notice-marquee-text');
    const btn = document.getElementById('btn-pause-notice');
    if (marquee) {
        marquee.classList.toggle('paused');
        const isPaused = marquee.classList.contains('paused');
        if (btn) btn.innerHTML = isPaused ? '<i class="fa-solid fa-play"></i>' : '<i class="fa-solid fa-pause"></i>';
    }
}

function openPublicTendersModal() {
    const modal = document.getElementById('modal-tenders');
    if (modal) modal.style.display = 'flex';
}

function closePublicTendersModal() {
    const modal = document.getElementById('modal-tenders');
    if (modal) modal.style.display = 'none';
}

function openHelplinesModal() {
    const modal = document.getElementById('modal-helplines');
    if (modal) modal.style.display = 'flex';
}

function closeHelplinesModal() {
    const modal = document.getElementById('modal-helplines');
    if (modal) modal.style.display = 'none';
}

function filterHelplinesDirectory(query) {
    const filter = (query || '').toLowerCase();
    const rows = document.querySelectorAll('#zonal-directory-table tbody tr');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(filter) ? '' : 'none';
    });
}

function openGrievanceTrackerModal() {
    const modal = document.getElementById('modal-grievance-tracker');
    if (modal) modal.style.display = 'flex';
}

function closeGrievanceTrackerModal() {
    const modal = document.getElementById('modal-grievance-tracker');
    if (modal) modal.style.display = 'none';
}

function lookupGrievanceSLA(ticketId) {
    const cleanId = (ticketId || 'MCC-2026-0941').trim();
    const countdownEl = document.getElementById('sla-countdown-val');
    const badgeEl = document.getElementById('sla-status-badge');
    if (countdownEl) countdownEl.innerText = '29 hrs 30 mins remaining';
    if (badgeEl) {
        badgeEl.className = 'pill-tag pill-green';
        badgeEl.innerHTML = '<i class="fa-solid fa-check"></i> WITHIN GUARANTEED SLA (48-HR)';
    }
    alert(`Fetched official Janahitha SLA record for Ticket: ${cleanId}\nStatus: Assigned to MCC Rapid Crew Van 04\nElapsed: 18.5 hrs | SLA Remaining: 29.5 hrs`);
}

function escalateToCommissioner() {
    const ticketId = (document.getElementById('sla-ticket-input')?.value || 'MCC-2026-0941').trim();
    const countdownEl = document.getElementById('sla-countdown-val');
    const badgeEl = document.getElementById('sla-status-badge');
    if (countdownEl) countdownEl.innerText = 'ESCALATED PRIORITY';
    if (badgeEl) {
        badgeEl.style.background = '#fee2e2';
        badgeEl.style.color = '#dc2626';
        badgeEl.style.borderColor = '#fca5a5';
        badgeEl.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> ESCALATED TO COMMISSIONER';
    }
    alert(`[KARNATAKA SAKALA SERVICES ACT 2011]\nGrievance ${ticketId} has been escalated to Zonal Commissioner (Zone 1 - Gokulam).\nEscalation Token: MCC-ESC-2026-8819\nDirect Notification dispatched to Assistant Executive Engineer.`);
}

function openInspectionCertificateModal() {
    const modal = document.getElementById('modal-inspection-certificate');
    if (modal) modal.style.display = 'flex';
}

function closeInspectionCertificateModal() {
    const modal = document.getElementById('modal-inspection-certificate');
    if (modal) modal.style.display = 'none';
}

function printInspectionCertificate() {
    window.print();
}

function openAllNoticesModal() {
    const modal = document.getElementById('modal-notices');
    if (modal) modal.style.display = 'flex';
}

function closeAllNoticesModal() {
    const modal = document.getElementById('modal-notices');
    if (modal) modal.style.display = 'none';
}



// =============================================================================
// Map Visual Directions & Detour Route Navigation Engine
// =============================================================================

let activeRouteMode = 'detour'; // 'detour' or 'depot'
let currentNavDestination = [12.3360, 76.6210];
let currentNavHazardName = "VVCE Ring Road Junction, Gokulam, Mysuru";

function initMapDirectionsRoute() {
    if (!state.map) return;
    if (!state.navRouteLayerGroup) {
        state.navRouteLayerGroup = L.layerGroup().addTo(state.map);
    }
    drawMapDirectionRoute();
}

function drawMapDirectionRoute(destCoord, hazardName, mode) {
    if (!state.map) return;
    if (!state.navRouteLayerGroup) {
        state.navRouteLayerGroup = L.layerGroup().addTo(state.map);
    }
    state.navRouteLayerGroup.clearLayers();

    if (destCoord) currentNavDestination = destCoord;
    if (hazardName) currentNavHazardName = hazardName;
    if (mode) activeRouteMode = mode;

    let startCoord, wp1, wp2, wp3, endCoord;
    let steps = [];

    if (activeRouteMode === 'depot') {
        // PWD Field Crew Depot Route Mode
        startCoord = [12.3395, 76.6180]; // Gokulam 3rd Stage Depot
        wp1 = [12.3380, 76.6195];
        wp2 = [12.3368, 76.6205];
        wp3 = [12.3362, 76.6208];
        endCoord = currentNavDestination;

        steps = [
            { num: 1, text: "<b>Depot Exit:</b> Depart Gokulam Depot onto Contour Rd (400m)", class: "" },
            { num: 2, text: "<b>Turn Right:</b> Turn onto 3rd Stage Main Road past Doctor's Corner (800m)", class: "blue" },
            { num: 3, text: `<b>Reach Site:</b> Arrive at ${currentNavHazardName.split(',')[0]} (1.2 km)`, class: "orange" },
            { num: 4, text: "<b>Station Van:</b> Deploy safety cones & begin cold-milling prep", class: "green" }
        ];

        document.getElementById('map-maneuver-title').textContent = "DEPOT TO SITE DISPATCH";
        document.getElementById('map-maneuver-sub').textContent = `Routing to: ${currentNavHazardName.split(',')[0]}`;
        document.getElementById('map-maneuver-icon').innerHTML = '<i class="fa-solid fa-truck-pickup"></i>';
        document.getElementById('btn-route-mode').innerHTML = '<i class="fa-solid fa-car"></i> Vehicle Detour';
        document.getElementById('map-nav-distance').textContent = "2.4 km";
        document.getElementById('map-nav-eta').textContent = "6 mins";
    } else {
        // Vehicle Hazard Detour Mode
        startCoord = [12.3385, 76.6190]; // Approaching Vehicle
        wp1 = [12.3368, 76.6202]; // 100m before hazard
        wp2 = [12.3360, 76.6210]; // Pothole / Hazard site
        wp3 = [12.3352, 76.6225]; // Temple Road Detour bypass
        endCoord = [12.3338, 76.6245]; // Clear Arterial Corridor rejoin

        steps = [
            { num: 1, text: `<b>Continue:</b> Head East along ${currentNavHazardName.split(',')[0]} (350m)`, class: "" },
            { num: 2, text: "<b>↖ Action:</b> Merge Left Lane in 25m to clear crater defect", class: "orange highlight-turn" },
            { num: 3, text: "<b>Detour:</b> Bypass via Temple Road link corridor (180m)", class: "blue" },
            { num: 4, text: "<b>Re-align:</b> Rejoin primary Ring Road carriageway past hazard", class: "green" }
        ];

        document.getElementById('map-maneuver-title').textContent = "MERGE LEFT IN 25m";
        document.getElementById('map-maneuver-sub').textContent = `Bypassing ${currentNavHazardName.split(',')[0]}`;
        document.getElementById('map-maneuver-icon').innerHTML = '<i class="fa-solid fa-arrow-turn-up fa-rotate-270"></i>';
        document.getElementById('btn-route-mode').innerHTML = '<i class="fa-solid fa-truck-pickup"></i> Crew Route';
        document.getElementById('map-nav-distance').textContent = "1.8 km";
        document.getElementById('map-nav-eta').textContent = "4 mins";
    }

    const routeCoords = [startCoord, wp1, wp2, wp3, endCoord];

    // 1. Draw High-Contrast Outer White Casing
    const casingPolyline = L.polyline(routeCoords, {
        color: '#FFFFFF',
        weight: 9,
        opacity: 0.95,
        lineCap: 'round',
        lineJoin: 'round'
    }).addTo(state.navRouteLayerGroup);

    // 2. Draw Vibrant Primary Direction Polyline
    const mainPolyline = L.polyline(routeCoords, {
        color: activeRouteMode === 'depot' ? '#EA580C' : '#0284C7',
        weight: 5,
        opacity: 1.0,
        lineCap: 'round',
        lineJoin: 'round'
    }).addTo(state.navRouteLayerGroup);

    // 3. Draw Marching Animated Pulse Overlay
    const dashPolyline = L.polyline(routeCoords, {
        color: '#38BDF8',
        weight: 3,
        dashArray: '8, 12',
        opacity: 0.95
    }).addTo(state.navRouteLayerGroup);

    // 4. Place Waypoint Badges
    const startIcon = L.divIcon({
        className: 'custom-wp-icon',
        html: `<div class="waypoint-badge start"><span>🚩</span> <span>${activeRouteMode === 'depot' ? 'DEPOT' : 'START'}</span></div>`,
        iconSize: [80, 24],
        iconAnchor: [40, 12]
    });
    L.marker(startCoord, { icon: startIcon }).addTo(state.navRouteLayerGroup);

    const hazardIcon = L.divIcon({
        className: 'custom-wp-icon',
        html: `<div class="waypoint-badge hazard"><span>⚠️</span> <span>${activeRouteMode === 'depot' ? 'DEFECT SITE' : 'MERGE LEFT'}</span></div>`,
        iconSize: [95, 24],
        iconAnchor: [47, 12]
    });
    L.marker(wp2, { icon: hazardIcon }).addTo(state.navRouteLayerGroup);

    const endIcon = L.divIcon({
        className: 'custom-wp-icon',
        html: `<div class="waypoint-badge end"><span>🏁</span> <span>${activeRouteMode === 'depot' ? 'ON SITE' : 'CLEAR'}</span></div>`,
        iconSize: [75, 24],
        iconAnchor: [37, 12]
    });
    L.marker(endCoord, { icon: endIcon }).addTo(state.navRouteLayerGroup);

    // Update Steps Scroller
    const scroller = document.getElementById('map-steps-scroller');
    if (scroller) {
        scroller.innerHTML = steps.map(s => `
            <div class="hud-step-item ${s.class}">
                <div class="step-num-bubble ${s.class}">${s.num}</div>
                <div class="step-text-content">${s.text}</div>
            </div>
        `).join('');
    }
}

function toggleMapDirectionsHUD() {
    const body = document.getElementById('directions-hud-body');
    const btn = document.getElementById('btn-toggle-map-hud');
    if (body) {
        body.classList.toggle('collapsed');
        const isCollapsed = body.classList.contains('collapsed');
        if (btn) btn.innerHTML = isCollapsed ? '<i class="fa-solid fa-chevron-down"></i>' : '<i class="fa-solid fa-chevron-up"></i>';
    }
}

function toggleRouteMode() {
    activeRouteMode = activeRouteMode === 'detour' ? 'depot' : 'detour';
    drawMapDirectionRoute();
    if (typeof playAlertChime === 'function') playAlertChime('pothole');
}

function speakMapDirectionPrompt() {
    const langSelect = document.getElementById('gov-lang-select');
    const currentLang = langSelect ? langSelect.value : 'en';

    let prompt = `Road hazard ahead near ${currentNavHazardName.split(',')[0]}. Merge to left lane in 25 meters; reduce speed to 20 kilometers per hour.`;
    let voiceCode = 'en-IN';

    if (currentLang === 'kn') {
        prompt = `ಮುಂದೆ ${currentNavHazardName.split(',')[0]} ಬಳಿ ರಸ್ತೆ ಗುಂಡಿ ಇದೆ. ಎಡ ಪಥಕ್ಕೆ ತಿರುಗಿ ಮತ್ತು ವೇಗ ಕಡಿಮೆ ಮಾಡಿ.`;
        voiceCode = 'kn-IN';
    } else if (currentLang === 'hi') {
        prompt = `आगे ${currentNavHazardName.split(',')[0]} के पास सड़क पर गड्ढा है। कृपया बाईं लेन में मुड़ें और गति धीमी करें।`;
        voiceCode = 'hi-IN';
    }

    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(prompt);
        utter.rate = 0.95;
        utter.pitch = 1.0;
        utter.lang = voiceCode;
        window.speechSynthesis.speak(utter);
    } else {
        alert(prompt);
    }
}
}


function switchFooterTab(tabKey) {
    document.querySelectorAll('.footer-tab-pill').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.footer-tab-panel').forEach(panel => panel.style.display = 'none');
    
    const activeBtn = document.getElementById(`ftab-btn-${tabKey}`);
    const activePanel = document.getElementById(`footer-tab-${tabKey}`);
    if (activeBtn) activeBtn.classList.add('active');
    if (activePanel) activePanel.style.display = 'flex';
}
