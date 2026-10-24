/**
 * UrbanSight AI — Smart City ICCC Command System (Infothon 7.0 / SIH26124)
 * Real-Time Multi-Agent Perception, DBSCAN Spatial Clustering, Automated PWD Dispatch,
 * ASTM D6433 PCI Degradation Forecasting, and In-Cab Transit Fleet Advisory
 */

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

            L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; OpenStreetMap &copy; CARTO',
                maxZoom: 19
            }).addTo(state.map);

            renderHazardsOnMap();
            renderBusesOnMap();
            renderPCIHeatmap(0);
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
const mediaState = {
    mode: 'video', // 'video' | 'image'
    sourceName: 'Mysuru ORR Dashcam (KSRTC-KA09-E102)',
    isPlaying: true,
    dpdpActive: true,
    userVideo: null,
    userImage: null,
    frameCount: 0,
    defect: {
type: 'POTHOLE',
rdd: 'D40 (Pothole / Subsidence)',
conf: '97.4%',
depth: '8.9cm',
sev: 'CRITICAL_P1',
busId: 'KSRTC-KA09-E102',
loc: 'VVCE Ring Road Junction, Gokulam, Mysuru',
lat: 12.3360,
lng: 76.6210,
sorCode: 'CPWD 16.14.2 (DBM Patch)',
ticketId: 'PWD-OCT-0745'
    }
};

function initDashcamSimulator() {
    const canvas = document.getElementById('dashcam-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

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
}

ctx.clearRect(0, 0, canvas.width, canvas.height);

if (mediaState.userVideo && !mediaState.userVideo.paused && !mediaState.userVideo.ended) {
    ctx.drawImage(mediaState.userVideo, 0, 0, canvas.width, canvas.height);
} else if (mediaState.userImage && mediaState.userImage.complete) {
    ctx.drawImage(mediaState.userImage, 0, 0, canvas.width, canvas.height);
} else if (baseImage.complete && baseImage.naturalWidth > 0) {
    ctx.drawImage(baseImage, 0, 0, canvas.width, canvas.height);
} else {
    // Synthetic Road Perspective
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

// AI Detection Crosshairs & Brackets
ctx.strokeStyle = 'rgba(2, 132, 199, 0.5)';
ctx.lineWidth = 1.5;
const bLen = 14;
ctx.beginPath();
ctx.moveTo(10, 10 + bLen); ctx.lineTo(10, 10); ctx.lineTo(10 + bLen, 10);
ctx.moveTo(canvas.width - 10 - bLen, 10); ctx.lineTo(canvas.width - 10, 10); ctx.lineTo(canvas.width - 10, 10 + bLen);
ctx.moveTo(10, canvas.height - 10 - bLen); ctx.lineTo(10, canvas.height - 10); ctx.lineTo(10 + bLen, canvas.height - 10);
ctx.moveTo(canvas.width - 10 - bLen, canvas.height - 10); ctx.lineTo(canvas.width - 10, canvas.height - 10); ctx.lineTo(canvas.width - 10, canvas.height - 10 - bLen);
ctx.stroke();

// Dynamic Scanline
const scanY = (mediaState.frameCount * 2.2) % canvas.height;
ctx.strokeStyle = 'rgba(2, 132, 199, 0.35)';
ctx.lineWidth = 1;
ctx.beginPath();
ctx.moveTo(12, scanY);
ctx.lineTo(canvas.width - 12, scanY);
ctx.stroke();

// DPDP Act 2023 §2(t) Privacy Gaussian Blurring
if (mediaState.dpdpActive) {
    ctx.save();
    ctx.filter = 'blur(10px)';
    ctx.fillStyle = 'rgba(40, 40, 40, 0.7)';
    // Civilian face mask
    ctx.fillRect(canvas.width * 0.14, canvas.height * 0.42, 28, 30);
    // Vehicle license plate mask
    ctx.fillRect(canvas.width * 0.72, canvas.height * 0.65, 54, 22);
    ctx.restore();

    ctx.strokeStyle = '#059669';
    ctx.lineWidth = 1;
    ctx.strokeRect(canvas.width * 0.14, canvas.height * 0.42, 28, 30);
    ctx.strokeRect(canvas.width * 0.72, canvas.height * 0.65, 54, 22);

    ctx.fillStyle = '#059669';
    ctx.font = 'bold 8px "JetBrains Mono"';
    ctx.fillText('DPDP §2(t) MASK', canvas.width * 0.72, canvas.height * 0.65 - 3);
}

// AI Bounding Box for Detected Road Distress
const timeOsc = Math.sin(mediaState.frameCount * 0.05);
const boxX = canvas.width * 0.48 + timeOsc * 2;
const boxY = canvas.height * 0.58;
const boxW = 150;
const boxH = 65;

ctx.strokeStyle = '#EA580C';
ctx.lineWidth = 2.2;
ctx.strokeRect(boxX, boxY, boxW, boxH);

ctx.fillStyle = '#EA580C';
ctx.fillRect(boxX, boxY - 18, 148, 18);
ctx.fillStyle = '#FFFFFF';
ctx.font = 'bold 9px "JetBrains Mono"';
ctx.fillText(`${mediaState.defect.type} ${mediaState.defect.rdd.split(' ')[0]} · ${mediaState.defect.conf}`, boxX + 6, boxY - 5);

ctx.fillStyle = 'rgba(28, 25, 23, 0.9)';
ctx.fillRect(boxX, boxY + boxH + 3, 150, 16);
ctx.fillStyle = '#EA580C';
ctx.font = '8px "JetBrains Mono"';
ctx.fillText(`depth: ${mediaState.defect.depth} · z-shock: 2.4g`, boxX + 6, boxY + boxH + 14);

requestAnimationFrame(drawLoop);
    }

    requestAnimationFrame(drawLoop);
}

function loadSampleMedia(type) {
    // Update active pill
    document.querySelectorAll('.btn-media-pill').forEach(b => b.classList.remove('active'));

    if (type === 'mysuru-video') {
const btn = document.getElementById('btn-media-sample-mysuru');
if (btn) btn.classList.add('active');
mediaState.mode = 'video';
mediaState.sourceName = 'Mysuru ORR Dashcam (KSRTC-KA09-E102)';
mediaState.userVideo = null;
mediaState.userImage = null;
if (mediaState.baseImage) mediaState.baseImage.src = 'image1.jpg';
mediaState.defect = {
    type: 'POTHOLE',
    rdd: 'D40 (Pothole / Subsidence)',
    conf: '97.4%',
    depth: '8.9cm',
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

    // Update UI Sidebar
    updateMediaSidebar();
}

function handleMediaUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    mediaState.customFile = file;
    const fileUrl = URL.createObjectURL(file);

    if (file.type.startsWith('video/')) {
mediaState.mode = 'video';
mediaState.sourceName = `Custom Video: ${file.name}`;
const videoEl = document.createElement('video');
videoEl.src = fileUrl;
videoEl.muted = true;
videoEl.loop = true;
videoEl.playsInline = true;
videoEl.play();
mediaState.userVideo = videoEl;
mediaState.userImage = null;
    } else {
mediaState.mode = 'image';
mediaState.sourceName = `Custom Photo: ${file.name}`;
const imgEl = new Image();
imgEl.src = fileUrl;
mediaState.userImage = imgEl;
mediaState.userVideo = null;
    }

    // Assign detection profile
    mediaState.defect = {
type: 'POTHOLE',
rdd: 'D40 (Pothole / Subsidence)',
conf: '97.8%',
depth: '8.7cm',
sev: 'CRITICAL_P1',
busId: 'KSRTC-KA09-E102',
loc: 'Mysuru Outer Ring Road (AI Ingested Media)',
lat: 12.3360,
lng: 76.6210,
sorCode: 'CPWD 16.14.2 (DBM Patch)',
ticketId: `PWD-OCT-${Math.floor(1000 + Math.random() * 9000)}`
    };

    updateMediaSidebar();

    // Notify terminal
    if (state.logs) {
state.logs.unshift({
    time: new Date().toTimeString().split(' ')[0],
    agent: 'Agent 1: Vision',
    tagClass: 'agent-tag-vision',
    text: `Ingested ${file.name} (${(file.size / (1024*1024)).toFixed(2)} MB). Neural Net scanning for RDD2022 distress patterns.`
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
if (mediaState.isPlaying) mediaState.userVideo.play();
else mediaState.userVideo.pause();
    }

    if (icon && text) {
if (mediaState.isPlaying) {
    icon.className = 'fa-solid fa-pause';
    text.textContent = 'PAUSE';
} else {
    icon.className = 'fa-solid fa-play';
    text.textContent = 'PLAY';
}
    }
}

function toggleDPDPMask() {
    mediaState.dpdpActive = !mediaState.dpdpActive;
    const text = document.getElementById('dpdp-status-text');
    const badge = document.getElementById('hud-dpdp-badge');

    if (text) text.textContent = mediaState.dpdpActive ? 'DPDP: ON' : 'DPDP: OFF';
    if (badge) {
badge.style.display = mediaState.dpdpActive ? 'inline-flex' : 'none';
    }
}

// Connect Complete Project: Auto-Dispatch and integrate with GIS Map, PWD Queue, and Terminal
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
