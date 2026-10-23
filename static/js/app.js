/**
 * UrbanSight AI — Smart City ICCC Command System (Infothon 7.0 / SIH26124)
 * Real-Time Multi-Agent Perception, DBSCAN Spatial Clustering, Automated PWD Dispatch & Fleet Advisory
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
        { id: "BMTC-KA01-E542", route: "Outer Ring Road Express (Silk Board ↔ Marathahalli)", lat: 12.9238, lng: 77.6745, speed: 32, heading: 45, marker: null },
        { id: "BMTC-KA57-E912", route: "Route 500D (Hebbal ↔ Electronic City)", lat: 12.9112, lng: 77.6380, speed: 26, heading: 180, marker: null },
        { id: "KSRTC-KA09-E102", route: "Mysuru Ring Road (VVCE Campus Corridor)", lat: 12.3160, lng: 76.6413, speed: 38, heading: 90, marker: null },
        { id: "BMTC-KA03-E304", route: "Majestic ↔ Whitefield ITPL Expressway", lat: 12.9716, lng: 77.5946, speed: 19, heading: 115, marker: null }
    ],
    hazards: [
        { id: "HAZ-001", type: "POTHOLE", sev: "CRITICAL_P1", lat: 12.9250, lng: 77.6760, name: "ORR Bellandur Flyover Pillar 34", depth: "9.4cm", conf: "96.4%", passes: 14, ticket: "PWD-OCT-0941", sorCode: "CPWD-16.14.2" },
        { id: "HAZ-002", type: "WATERLOGGING", sev: "HIGH_P2", lat: 12.9125, lng: 77.6395, name: "Silk Board Underpass South Lane", length: "35m", conf: "92.1%", passes: 8, ticket: "PWD-OCT-0882", sorCode: "CPWD-11.4.2" },
        { id: "HAZ-003", type: "POTHOLE", sev: "CRITICAL_P1", lat: 12.3190, lng: 76.6450, name: "VVCE Ring Road Junction, Mysuru", depth: "8.6cm", conf: "94.8%", passes: 6, ticket: "PWD-OCT-0715", sorCode: "CPWD-16.14.2" },
        { id: "HAZ-004", type: "CONGESTION", sev: "MEDIUM_P3", lat: 12.9730, lng: 77.5960, name: "Kasturba Road Bottleneck (9 km/h)", conf: "88.5%", passes: 12, ticket: null, sorCode: "TRAFFIC-CORRIDOR" }
    ],
    workOrders: [
        { ticket: "PWD-OCT-0941", type: "POTHOLE", sev: "CRITICAL_P1", loc: "ORR Bellandur Flyover Pillar 34", passes: 14, sla: "41h 20m remaining", status: "DISPATCHED", sorCode: "CPWD 16.14.2 (DBM Patch)" },
        { ticket: "PWD-OCT-0882", type: "WATERLOGGING", sev: "HIGH_P2", loc: "Silk Board Underpass South Lane", passes: 8, sla: "19h 45m remaining", status: "CREW_ASSIGNED", sorCode: "CPWD 11.4.2 (Drain De-silt)" },
        { ticket: "PWD-OCT-0715", type: "POTHOLE", sev: "CRITICAL_P1", loc: "VVCE Ring Road Junction, Mysuru", passes: 6, sla: "44h 10m remaining", status: "IN_PROGRESS", sorCode: "CPWD 16.14.2 (DBM Patch)" }
    ],
    logs: [
        { time: "19:54:10", agent: "Agent 1: Vision", tagClass: "agent-tag-vision", text: "YOLOv8-Nano running @ 30 FPS. DPDP Gaussian face & plate blur ACTIVE." },
        { time: "19:54:02", agent: "Agent 2: DBSCAN", tagClass: "agent-tag-dbscan", text: "Clustered 14 bus passes into canonical hazard #HAZ-001 (5m epsilon match)." },
        { time: "19:53:50", agent: "Agent 3: PWD Dispatch", tagClass: "agent-tag-dispatch", text: "Auto-filed PWD Work Order #PWD-OCT-0941 with GPS & photo evidence (<180s SLA)." },
        { time: "19:53:35", agent: "Agent 4: Fleet Advisory", tagClass: "agent-tag-advisory", text: "Pushed WebSocket warning alert to oncoming buses on Bellandur corridor." }
    ],
    settings: {
        privacyBlur: true
    },
    map: null
};

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
    }).setView([12.9350, 77.6400], 12);

    // CartoDB Dark Matter Tiles
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        maxZoom: 19
    }).addTo(state.map);

    renderHazardsOnMap();
    renderBusesOnMap();
}

function renderHazardsOnMap() {
    if (!state.map) return;
    state.hazards.forEach(h => {
        let color = '#FF9500';
        let iconClass = 'fa-triangle-exclamation';

        if (h.type === 'POTHOLE') {
            color = h.sev === 'CRITICAL_P1' ? '#FF3B30' : '#FF9500';
            iconClass = 'fa-road';
        } else if (h.type === 'WATERLOGGING') {
            color = '#00F0FF';
            iconClass = 'fa-water';
        } else if (h.type === 'CONGESTION') {
            color = '#AF52DE';
            iconClass = 'fa-car';
        }

        const markerHtml = `
            <div style="position:relative; width:32px; height:32px; display:flex; align-items:center; justify-content:center;">
                <div style="position:absolute; width:100%; height:100%; border-radius:50%; background:${color}; opacity:0.3; animation:livePulse 1.8s infinite;"></div>
                <div style="width:22px; height:22px; border-radius:50%; background:${color}; color:#070A11; display:flex; align-items:center; justify-content:center; font-size:11px; font-weight:800; box-shadow:0 0 14px ${color};">
                    <i class="fa-solid ${iconClass}"></i>
                </div>
            </div>
        `;

        const hazardIcon = L.divIcon({
            className: 'hazard-custom-marker',
            html: markerHtml,
            iconSize: [32, 32]
        });

        const voucherLink = h.ticket ? `<div style="margin-top:8px; border-top:1px solid rgba(255,255,255,0.08); padding-top:6px;"><a href="voucher.html?ticket=${h.ticket}" target="_blank" style="color:#00F0FF; font-size:11px; font-weight:700; text-decoration:none;"><i class="fa-solid fa-file-invoice"></i> View CPWD Voucher #${h.ticket} &rarr;</a></div>` : '';

        const popupContent = `
            <div style="color:#F5F7FA; font-family:'Plus Jakarta Sans',sans-serif; min-width:200px; padding:4px;">
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:6px;">
                    <span style="font-weight:800; font-size:11px; color:${color}; font-family:'JetBrains Mono';">[${h.sev}] ${h.type}</span>
                    <span style="font-size:10px; color:#9BA3AF; font-family:'JetBrains Mono';">${h.conf}</span>
                </div>
                <div style="font-size:12px; font-weight:600; margin-bottom:6px; color:#FFFFFF;">${h.name}</div>
                <div style="font-size:11px; color:#9BA3AF; display:flex; flex-direction:column; gap:2px;">
                    ${h.depth ? `<div>Measured Depth: <b style="color:#F5F7FA;">${h.depth}</b></div>` : ''}
                    ${h.length ? `<div>Submerged Length: <b style="color:#F5F7FA;">${h.length}</b></div>` : ''}
                    <div>DBSCAN Cluster Passes: <b style="color:#00F0FF;">${h.passes} passes verified</b></div>
                    ${h.sorCode ? `<div>CPWD SOR Code: <b style="color:#FF9500;">${h.sorCode}</b></div>` : ''}
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
        const busHtml = `
            <div style="background:#00F0FF; color:#070A11; border-radius:50%; width:28px; height:28px; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:800; box-shadow:0 0 16px rgba(0,240,255,0.6); border:2px solid #FFFFFF;">
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
                <div style="color:#F5F7FA; font-family:'Plus Jakarta Sans',sans-serif; min-width:180px; padding:4px;">
                    <div style="font-weight:800; font-size:12px; color:#00F0FF; font-family:'JetBrains Mono';">${b.id}</div>
                    <div style="font-size:11px; margin:4px 0 6px; color:#FFFFFF;">${b.route}</div>
                    <div style="font-size:10px; color:#34C759; font-weight:600;">● CAMERA: ONLINE (30 FPS)</div>
                    <div style="font-size:10px; color:#9BA3AF; margin-top:2px;">Speed: ${b.speed} km/h • Heading: ${b.heading}°</div>
                    <div style="font-size:10px; color:#9BA3AF;">Privacy: <b style="color:#34C759;">DPDP ACT 2023 §2(t) MASK ON</b></div>
                </div>
            `)
            .addTo(state.map);
    });
}

// 3. Live Edge Dashcam Vision Canvas Simulator
function initDashcamSimulator() {
    const canvas = document.getElementById('dashcam-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let frameCount = 0;
    const baseImage = new Image();
    baseImage.crossOrigin = "anonymous";
    baseImage.onerror = () => {
        if (!baseImage.src.includes('static/')) {
            baseImage.src = '/static/image1.jpg';
        }
    };
    baseImage.src = 'image1.jpg';

    function drawFrame() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // 1. Draw base photo or procedural high-tech highway
        if (baseImage.complete && baseImage.naturalWidth > 0) {
            ctx.drawImage(baseImage, 0, 0, canvas.width, canvas.height);
        } else {
            // Procedural night expressway
            const grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
            grad.addColorStop(0, '#0F1626');
            grad.addColorStop(0.45, '#0B0F1A');
            grad.addColorStop(1, '#05070E');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Perspective Road Lines
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(canvas.width * 0.46, canvas.height * 0.38);
            ctx.lineTo(canvas.width * 0.08, canvas.height);
            ctx.moveTo(canvas.width * 0.54, canvas.height * 0.38);
            ctx.lineTo(canvas.width * 0.92, canvas.height);
            ctx.stroke();

            // Center lane markings (animated dashes)
            ctx.strokeStyle = 'rgba(255, 200, 0, 0.25)';
            ctx.lineWidth = 2;
            ctx.setLineDash([12, 16]);
            ctx.lineDashOffset = -frameCount * 3;
            ctx.beginPath();
            ctx.moveTo(canvas.width * 0.5, canvas.height * 0.38);
            ctx.lineTo(canvas.width * 0.5, canvas.height);
            ctx.stroke();
            ctx.setLineDash([]);
        }

        // 2. Optical Reticles & Corner Alignment Brackets
        const bracketColor = 'rgba(0, 240, 255, 0.4)';
        ctx.strokeStyle = bracketColor;
        ctx.lineWidth = 1.5;
        const bLen = 14;

        // Top-left bracket
        ctx.beginPath();
        ctx.moveTo(10, 10 + bLen); ctx.lineTo(10, 10); ctx.lineTo(10 + bLen, 10);
        // Top-right bracket
        ctx.moveTo(canvas.width - 10 - bLen, 10); ctx.lineTo(canvas.width - 10, 10); ctx.lineTo(canvas.width - 10, 10 + bLen);
        // Bottom-left bracket
        ctx.moveTo(10, canvas.height - 10 - bLen); ctx.lineTo(10, canvas.height - 10); ctx.lineTo(10 + bLen, canvas.height - 10);
        // Bottom-right bracket
        ctx.moveTo(canvas.width - 10 - bLen, canvas.height - 10); ctx.lineTo(canvas.width - 10, canvas.height - 10); ctx.lineTo(canvas.width - 10, canvas.height - 10 - bLen);
        ctx.stroke();

        // Subtle horizon crosshair
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(canvas.width * 0.5 - 15, canvas.height * 0.5);
        ctx.lineTo(canvas.width * 0.5 + 15, canvas.height * 0.5);
        ctx.moveTo(canvas.width * 0.5, canvas.height * 0.5 - 15);
        ctx.lineTo(canvas.width * 0.5, canvas.height * 0.5 + 15);
        ctx.stroke();

        const timeOsc = Math.sin(frameCount * 0.04);

        // 3. Pothole D40 AI Bounding Box (Amber / Red with Corner Accents)
        const potX = canvas.width * 0.56 + timeOsc * 1.5;
        const potY = canvas.height * 0.61;
        const potW = 148;
        const potH = 68;

        // Box border with glow
        ctx.strokeStyle = '#FF9500';
        ctx.lineWidth = 2;
        ctx.strokeRect(potX, potY, potW, potH);

        // Header Tag
        ctx.fillStyle = '#FF9500';
        ctx.fillRect(potX, potY - 20, 142, 20);
        ctx.fillStyle = '#070A11';
        ctx.font = 'bold 9px "JetBrains Mono"';
        ctx.fillText('POTHOLE D40 · 96.4%', potX + 6, potY - 6);

        // Metric Sub-badge
        ctx.fillStyle = 'rgba(7, 10, 17, 0.85)';
        ctx.fillRect(potX, potY + potH + 4, 148, 16);
        ctx.fillStyle = '#FF9500';
        ctx.font = '8px "JetBrains Mono"';
        ctx.fillText('depth: 9.8cm · z-shock: 2.4g', potX + 6, potY + potH + 15);

        // 4. Waterlogging D80 AI Bounding Box (Electric Cyan)
        const watX = canvas.width * 0.18 - timeOsc * 1.5;
        const watY = canvas.height * 0.52;
        const watW = 155;
        const watH = 58;

        ctx.strokeStyle = '#00F0FF';
        ctx.lineWidth = 2;
        ctx.strokeRect(watX, watY, watW, watH);

        ctx.fillStyle = '#00F0FF';
        ctx.fillRect(watX, watY - 20, 148, 20);
        ctx.fillStyle = '#070A11';
        ctx.font = 'bold 9px "JetBrains Mono"';
        ctx.fillText('WATERLOGGING · 92.1%', watX + 6, watY - 6);

        ctx.fillStyle = 'rgba(7, 10, 17, 0.85)';
        ctx.fillRect(watX, watY + watH + 4, 145, 16);
        ctx.fillStyle = '#00F0FF';
        ctx.font = '8px "JetBrains Mono"';
        ctx.fillText('length: 35.0m · lane 1', watX + 6, watY + watH + 15);

        // 5. On-Device DPDP Gaussian Privacy Mask (Faces & Vehicle Plates)
        if (state.settings.privacyBlur) {
            const blurX = canvas.width * 0.10;
            const blurY = canvas.height * 0.44;
            const blurW = 42;
            const blurH = 50;

            // Pixelated/Frosted fill
            ctx.fillStyle = 'rgba(20, 28, 48, 0.88)';
            ctx.fillRect(blurX, blurY, blurW, blurH);

            // Crosshatch texture
            ctx.strokeStyle = 'rgba(52, 199, 89, 0.25)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            for (let i = 0; i < blurW; i += 6) {
                ctx.moveTo(blurX + i, blurY);
                ctx.lineTo(blurX + i, blurY + blurH);
            }
            ctx.stroke();

            // Green bounding border
            ctx.strokeStyle = '#34C759';
            ctx.lineWidth = 1.5;
            ctx.strokeRect(blurX, blurY, blurW, blurH);

            // DPDP Label
            ctx.fillStyle = '#34C759';
            ctx.font = 'bold 7px "JetBrains Mono"';
            ctx.fillText('DPDP BLUR', blurX + 2, blurY - 4);
        }

        frameCount++;
        requestAnimationFrame(drawFrame);
    }

    drawFrame();
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
    // 1. Simulate Bus Pass Button
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

    // 2. Trigger Driver Alert Direct Button
    const btnAlert = document.getElementById('btn-driver-alert');
    if (btnAlert) {
        btnAlert.addEventListener('click', () => {
            triggerDriverAlert("CRITICAL POTHOLE (9.4cm Depth)", "Outer Ring Road near Bellandur Flyover (150m Ahead)", "Slow down to 20 km/h; move to center lane.");
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
    if (modalOverlay) {
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) modalOverlay.classList.remove('show');
        });
    }

    // 4. Privacy Toggle Button
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

    // 5. Export CSV Button
    const btnCsv = document.getElementById('btn-export-csv');
    if (btnCsv) {
        btnCsv.addEventListener('click', (e) => {
            e.preventDefault();
            exportCSV();
        });
    }

    // 6. Export GeoJSON Button
    const btnGeo = document.getElementById('btn-export-geojson');
    if (btnGeo) {
        btnGeo.addEventListener('click', (e) => {
            e.preventDefault();
            exportGeoJSON();
        });
    }
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
