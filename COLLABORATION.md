# UrbanSight AI — Multi-Agent GitHub Collaboration Board
**Infothon 7.0 · Problem Statement #07 · SIH26124**
**Team: Vidyavardhaka College of Engineering (VVCE), Mysuru**

---

## 🏛️ System Architecture & Team Roles

| Node | Computer | Owner | Primary Focus | Active Branches |
| :--- | :--- | :--- | :--- | :--- |
| **Node A (Command Center)** | Computer A (Master) | Gagan K S | ICCC Backend, FastAPI, DBSCAN Clustering, CPWD Municipal Dispatch, Main Dashboard | `main`, `gh-pages` |
| **Node B (Edge Specialist)** | Computer B (Worker) | Teammate | Edge Perception Engine, Driver In-Cab Console, Multi-Route Simulation, Benchmarks | `feature/edge-driver-hud`, `main` |

---

## 📜 Git Collaboration Rules
1. **Never break existing contracts**: Do not alter `backend/models.py` or existing endpoints in `backend/main.py` without consulting Node A.
2. **Test Before Pushing**: Always verify `python -m unittest tests/test_pipeline.py` returns 24/24 passed (100%) before committing.
3. **Commit Convention**: Use clear commit prefixes: `feat:`, `fix:`, `docs:`, `perf:`, `test:`.
4. **Autonomous Execution**: Pick the next unassigned task below, implement it completely, test it, mark it `[COMPLETED]`, and push to GitHub.

---

## 📋 Task Dispatch Queue

### 🟢 TASK-01: In-Cab Driver HUD Console UI [COMPLETED]
- **Assignee**: Node B (Teammate Antigravity)
- **Target File**: `frontend/driver_console.html` (or `templates/driver_console.html` + standalone `driver_console.html` at root for GitHub Pages)
- **Objective**: Create a high-contrast, distraction-free tablet UI designed for the bus driver's dashboard mount.
- **Requirements**:
  1. **Visual Style**: Dark mode high-contrast (JetBrains Mono + Plus Jakarta Sans, neon cyan `#00E5FF`, warning amber `#F59E0B`, alert red `#EF4444`).
  2. **Driver Gauges**: Current bus ID (`BMTC-KA57-E912`), route name (`Route 500D - Hebbal ↔ Silk Board`), live speedometer (e.g. 38 km/h), GPS coordinates, and camera status (`DPDP Privacy Mask: ACTIVE`).
  3. **Hazard Advisory Card**: Displays upcoming hazard within 300m:
     - Warning type (e.g. "CRITICAL POTHOLE - 9.4cm Depth").
     - Countdown distance meter (e.g., "180m Ahead", decreases dynamically).
     - Recommended Action (e.g., "Merge to Left Lane; Reduce speed to 20 km/h").
     - Dynamic lane arrow icon (left merge / right merge / slow down).
  4. **Audio Alert Simulator**: Web Audio API beep chime button for incoming critical alerts.
  5. **Data Integration**: Connects via fetch to `/api/buses/BMTC-KA57-E912/telemetry` when running locally, and includes automatic demo fallback when viewed on GitHub Pages.

---

### 🟢 TASK-02: Multi-Route Karnataka GPS Telemetry Generator [COMPLETED]
- **Assignee**: Node B (Teammate Antigravity)
- **Target Files**: `distributed/routes/bmtc_orr.json`, `distributed/routes/bmtc_ecity.json`, `distributed/routes/mysuru_ringroad.json`
- **Objective**: Provide realistic high-frequency GPS coordinate sequences with road elevation changes and simulated IMU z-axis profiles.
- **Requirements**:
  1. `bmtc_orr.json`: Outer Ring Road (Hebbal ➔ Marathahalli ➔ Bellandur ➔ Silk Board) with 50+ coordinate waypoints.
  2. `bmtc_ecity.json`: Silk Board ➔ Electronic City Elevated Tollway with 40+ waypoints.
  3. `mysuru_ringroad.json`: VVCE Mysuru ➔ Hunsur Road Junction ➔ Columbia Asia Hospital Ring Road with 40+ waypoints.
  4. Update `distributed/edge_bus_node.py` to accept `--route <route_file>` argument to stream real transit trajectories!

---

### 🟢 TASK-03: Edge Hardware & AI Model Benchmarking Suite [COMPLETED]
- **Assignee**: Node B (Teammate Antigravity)
- **Target File**: `distributed/edge_benchmark.py`
- **Objective**: Run automated benchmarks on the local CPU/GPU to measure real edge performance metrics for the presentation slide.
- **Requirements**:
  1. Test simulated YOLOv8-Nano inference latency across 100 iterations (measure mean, p95, p99 ms and FPS).
  2. Test DPDP Gaussian face/plate blurring latency (measure processing overhead in ms).
  3. Test DBSCAN spatial clustering execution time on 100 sample coordinates.
  4. Output a clean markdown summary table directly printable in `distributed/BENCHMARK_RESULTS.md`.

---

### 🟢 TASK-04: Public Citizen Repair Tracking Portal [COMPLETED]
- **Assignee**: Node B (Teammate Antigravity)
- **Target File**: `citizen_portal.html` (root) & `templates/citizen_portal.html`
- **Objective**: Create a citizen-facing lookup page with search bar to track PWD road repair status.
- **Requirements**:
  1. Status Stepper: [1. Spotted by Bus Dashcam] -> [2. Multi-Pass Verified] -> [3. PWD Work Order Dispatched] -> [4. Repair In Progress] -> [5. Closed].
  2. Ward Information: BBMP Mahadevapura Ward 85 / MCC Mysuru Ward 9.
  3. SLA countdown timer (e.g., "38h 15m remaining").
  4. DPDP-blurred camera snapshot preview with bounding box.
  5. "Notify Me on WhatsApp / SMS" button mockup.
  6. Hybrid API integration connecting to `/api/work-orders` with fallback sample dataset for static GitHub Pages.

---

### 🟢 TASK-05: CPWD Voucher API & Resolution Endpoints [COMPLETED]
- **Assignee**: Node A (Gagan Antigravity) & Node B
- **Target Files**: `backend/main.py`, `backend/agents/municipal_dispatcher.py`
- **Objective**: Implement backend endpoints for itemized CPWD tender calculation, resolution state transitions, and CSV exports.
- **Requirements**:
  1. Add `GET /api/work-orders/{ticket_id}/voucher` returning itemized CPWD SOR 2024 breakdown (base rate, labor, GST 18%, penalty SLA clauses).
  2. Add `POST /api/work-orders/{ticket_id}/resolve` and `POST /api/work-orders/{ticket_id}/status` allowing field crews to update ticket status (`IN_PROGRESS`, `RESOLVED`) with repair remarks and timestamp.
  3. Add `GET /api/export-csv` exporting all work orders and hazards in clean tabular format for municipal engineers.
  4. Mount routes `/citizen`, `/field-crew`, and `/voucher` to serve the respective HTML templates.

---

### 🟢 TASK-06: Mobile Field Crew PWA & Official Printable Voucher UI [COMPLETED]
- **Assignee**: Node B (Teammate Antigravity) & Node A
- **Target Files**: `field_crew.html`, `templates/field_crew.html`, `voucher.html`, `templates/voucher.html`
- **Objective**: Build mobile-friendly field technician resolution PWA and printable government CPWD voucher.
- **Requirements**:
  1. `field_crew.html`: Mobile PWA for PWD vans showing nearby assigned work orders, GPS distance, Before/After photo audit, and `[Start Repair]` / `[Complete & Close]` state buttons.
  2. `voucher.html`: Printable government letterhead tender voucher with QR code, CPWD Schedule of Rates line items, and contractor signature sign-off.
  3. Seamless hybrid integration connecting to Node A's `/api/work-orders/{id}/resolve` with offline demo fallback.

---

### 🟢 TASK-07: Pavement Condition Index (PCI) & Degradation Forecasting Heatmap [COMPLETED]
- **Assignee**: Node B (Teammate Antigravity)
- **Target Files**: `backend/agents/pci_engine.py`, `backend/main.py`, `static/js/app.js`, `templates/index.html`, `index.html`
- **Objective**: Implement ASTM D6433 standard road health scoring and predictive asphalt decay model with Leaflet GIS corridor visualization.
- **Requirements**:
  1. `backend/agents/pci_engine.py`: Markov chain exponential asphalt decay $PCI(t) = PCI_0 \cdot e^{-kt}$ clamped between 10 and 100 with ASTM rating bands (Good >=80, Fair >=65, Poor >=40, Critical <40) and CPWD maintenance cost estimators.
  2. `backend/main.py`: Endpoints `GET /api/pci-heatmap?days=0` and `GET /api/pci-summary?days=0` returning geo-corridor polylines and executive municipal ROI.
  3. Interactive Leaflet GIS Heatmap with floating forecast bar (`Day 0`, `+14 Days`, `+30 Days`) showing real-time road condition degradation and cost escalation.
  4. 100% test coverage in `tests/test_pipeline.py` (25/25 passing).

---

### 🟢 TASK-08: Municipal Ward Governance & Maintenance ROI Analytics Dashboard [COMPLETED]
- **Assignee**: Node B (Teammate Antigravity)
- **Target Files**: `analytics.html`, `templates/analytics.html`, `backend/main.py`, `tests/test_pipeline.py`
- **Objective**: Executive command view for Municipal Commissioners & Chief Engineers tracking ward SLA adherence, MTTR, defect composition, and predictive maintenance budget savings.
- **Requirements**:
  1. `backend/main.py`: Route `GET /analytics` and API `GET /api/analytics/ward-summary` returning ward rankings, defect compositions, MTTR, and cumulative savings.
  2. `analytics.html` & `templates/analytics.html`: Full-featured executive dashboard with KPI ribbons, interactive ULB/Ward filter, SLA performance leaderboard, defect composition bars, and 8.4x ROI savings calculator.
  3. One-click `@media print` A4 printable executive report format.
  4. 100% test pass rate in `tests/test_pipeline.py` (28/28 tests passing).

---

### 🟢 TASK-09: Ultra-Modern Minimal Tech Design System & Frontend UI/UX Overhaul [COMPLETED]
- **Assignee**: Lead Frontend UI/UX Architect (Antigravity)
- **Target Files**: index.html, 	emplates/index.html, static/css/style.css, static/js/app.js, citizen_portal.html, oucher.html
- **Objective**: Overhaul the frontend into a stunning, branded, ultra-modern, minimal tech aesthetic inspired by Linear, Vercel, Apple, and Palantir Foundry dark mode.
- **Key Deliverables**:
  1. **Visual Identity & Design Tokens**: Obsidian depth (#070A11, #0D111D), glassmorphic panels (rgba(13, 17, 29, 0.75) with 16px blur and hairline borders), electric cyan (#00F0FF) with soft glow, vivid amber (#FF9500), and emerald green (#34C759).
  2. **Unified Smart City Portal Switcher**: Floating pill nav linking all smart city portals (Command Center, Driver HUD, Citizen Portal, Field Crew PWA, CPWD Voucher, Ward Analytics).
  3. **High-Impact 4-Card KPI Strip**: Fleets Online (10,000 e-Buses), Distance Scanned (4,820 km), Autonomous PWD Dispatches (3 Active), Privacy Compliance (100% DPDP Act 2023 §2(t)).
  4. **Cutting-Edge Dashcam HUD**: Realistic telemetry, corner crosshairs, smooth AI bounding boxes, and prominent DPDP Gaussian privacy badge.
  5. **Terminal Decision Feed & PWD Queue**: Modern terminal with agent color tags, CPWD SOR codes, dynamic SLA countdowns, and direct voucher links.
  6. **Interactive Offline Exports**: Direct client-side CSV and RFC 7946 GeoJSON export blob generators guaranteeing 100% reliability on standalone GitHub Pages.
  7. **Full Synchronization**: Both main and gh-pages updated and 28/28 unit tests passing.

---

### 🟢 TASK-10: Warm Beige Light Design System & Branded Ecosystem UI [COMPLETED]
- **Assignee**: Lead Frontend UI/UX Architect (Antigravity)
- **Target Files**: All 6 HTML portals + Jinja2 templates (`index.html`, `citizen_portal.html`, `field_crew.html`, `driver_console.html`, `analytics.html`, `voucher.html`, `COLLABORATION.md`)
- **Objective**: Implement a refined, government-grade warm beige light theme paired with official branded icons (NVIDIA Jetson, GitHub, transit agencies BMTC & KSRTC, municipal civic crests BBMP & MCC, and custom UrbanSight AI mobility perception SVG emblems).
- **Key Deliverables**:
  1. **Color Palette**: Warm linen background (`#F5F2EB`), creamy ivory surfaces (`#FAF8F5`), high-contrast stone 900 charcoal typography (`#1C1917`), and CartoDB Voyager GIS map styling.
  2. **Custom Vector Emblem**: Clean 4-layer SVG perception emblem rendered across all portal navigation bars and headers.
  3. **Official Hardware & Agency Branding**:
     - NVIDIA Jetson Orin Nano hardware badge (`fa-brands fa-nvidia`, `#76B900`).
     - Open source repository navigation links (`fa-brands fa-github`).
     - Transit & Municipal badges: BMTC, KSRTC, BBMP, MCC, CPWD SOR 2024, and DPDP Act 2023.
  4. **Full Test Suite & Dual-Branch Synchronization**: 28/28 unit tests passing, synced across `main` and `gh-pages`.

## 🔄 Status Tracker
- [x] Backend 4-Agent Modular Architecture (`tests/test_pipeline.py` 24/24 passing) — Node A & B
- [x] Real-time GIS Command Dashboard (`index.html`) — Node A
- [x] OGC GeoJSON Export (`/api/export-geojson`) — Node A
- [x] TASK-01: In-Cab Driver HUD Console UI (`driver_console.html`, `templates/driver_console.html`) — Node B (Completed)
- [x] TASK-02: Multi-Route Karnataka GPS Telemetry (`distributed/routes/*.json`) — Node B (Completed)
- [x] TASK-03: Edge Hardware & AI Model Benchmark Suite (`distributed/edge_benchmark.py`, `BENCHMARK_RESULTS.md`) — Node B (Completed)
- [x] TASK-04: Public Citizen Repair Tracking Portal (`citizen_portal.html`, `templates/citizen_portal.html`) — Node B (Completed)
- [x] TASK-05: CPWD Voucher API & Resolution Endpoints (`/api/work-orders/{id}/voucher`, `/api/export-csv`, `/api/work-orders/{id}/resolve`) — Node A & B (Completed)
- [x] TASK-06: Mobile Field Crew PWA & Printable Voucher UI (`field_crew.html`, `voucher.html`) — Node B & A (Completed)
- [x] TASK-07: Pavement Condition Index (PCI) & Degradation Forecasting Heatmap (`backend/agents/pci_engine.py`, `index.html`) — Node B (Completed)
- [x] TASK-08: Municipal Ward Governance & Maintenance ROI Analytics Dashboard (`analytics.html`, `templates/analytics.html`) — Node B (Completed)
- [x] TASK-09: Ultra-Modern Minimal Tech Design System & Frontend UI/UX Overhaul (index.html, style.css, pp.js) — Lead Frontend UI/UX Architect (Completed)
- [x] TASK-10: Warm Beige Light Design System & Branded Ecosystem UI (All 6 HTML portals + templates) — Lead Frontend UI/UX Architect (Completed)
