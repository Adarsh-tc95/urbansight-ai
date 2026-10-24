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

---

### 🟢 TASK-11: Mysuru GIS Map Integration & Realistic Civic Iconography [COMPLETED]
- **Assignee**: Lead Frontend UI/UX Architect (Antigravity)
- **Target Files**: `index.html`, `templates/index.html`, `static/js/app.js`, `citizen_portal.html`, `driver_console.html`, `backend/agents/pci_engine.py`, `backend/simulated_data.py`, `COLLABORATION.md`
- **Objective**: Integrate interactive Mysuru City Corporation (MCC) & MUDA GIS mapping with realistic physical iconography (tangible 3D teardrop road distress pins, fleet bus vehicle capsule markers, and authentic civic shield SVG crests with perspective roads and electric transit buses), removing all synthetic AI-style wireframes.
- **Key Deliverables**:
  1. **Mysuru GIS Map Canvas**: Map default-centered on Mysuru (`[12.3360, 76.6210]`, zoom 13) with interactive City Switcher (`Mysuru MCC`, `Bengaluru BBMP`, `All Karnataka Transit`).
  2. **Mysuru Landmark Navigation**: Quick-jump buttons for VVCE Gokulam Campus, Hunsur Road Signal, Columbia Asia Junction, Chamundi Foothills, and Infosys Campus.
  3. **Realistic Tangible Markers**: 3D teardrop location pins with downward anchor shadows and authentic distress glyphs; fleet vehicle markers with KSRTC Mysuru / BMTC ORR registration plates and live telemetry pulses.
  4. **Driver In-Cab HUD Route Toggle**: Live toggle between Bengaluru Route 500D and Mysuru Ring Road (VVCE ↔ Columbia Asia).
  5. **100% Test Pass Rate & Full Sync**: 28/28 unit tests passing, synced across `main` and `gh-pages`.

---

### 🟢 TASK-12: Transit Video & Photo Road Inspection AI Analyzer Engine [COMPLETED]
- **Assignee**: Lead Vision & Fullstack Engineer (Antigravity)
- **Target Files**: `backend/main.py`, `tests/test_pipeline.py`, `index.html`, `templates/index.html`, `static/js/app.js`, `COLLABORATION.md`
- **Objective**: Implement comprehensive end-to-end video and photo analysis where users can upload or stream dashcam video footage and road distress photographs, run real-time YOLOv8/v10 RDD2022 inference with DPDP Act 2023 §2(t) face/plate blurring, and automatically connect the detection to the full multi-agent grid (GIS map pin drop, PWD dispatch, CPWD voucher generation, and in-cab advisory).
- **Key Deliverables**:
  1. **Dual Ingestion Engine**: Supports custom video (`.mp4`, `.webm`, `.mov`) and photo (`.jpg`, `.png`) uploads plus 4 instant sample transit feeds (Mysuru ORR Dashcam, Bengaluru 500D Feed, Hunsur Road Pothole Photo, Silk Board Flood Photo).
  2. **Real-Time Video Playback & HUD Scanning**: HTML5 canvas video rendering with animated scanlines, live bounding box overlays, distress metrics (depth cm, length m, severity P1/P2), and DPDP Gaussian privacy blur masks.
  3. **End-to-End Grid Dispatch Connection**: Single-click "Run AI Analysis & Auto-Dispatch to PWD Grid" button connects to Leaflet GIS (drops realistic 3D pin & flies to location), PWD work orders queue, Terminal Decision Feed, and generates an official printable CPWD tender voucher.
  4. **Backend REST API**: Endpoints `POST /api/analyze-media` (multipart upload) and `POST /api/analyze-media-json` passing detections through `orchestrator.process_edge_detection()`.
  5. **100% Test Coverage**: 29/29 unit tests passing, synced across `main` and `gh-pages`.

---

### 🟢 TASK-13: Automated WhatsApp & SMS Municipal Alert Notification Gateway [COMPLETED]
- **Assignee**: Lead Messaging & Fullstack Systems Engineer (Antigravity)
- **Target Files**: backend/main.py, tests/test_pipeline.py, index.html, templates/index.html, static/js/app.js, citizen_portal.html, templates/citizen_portal.html, voucher.html, templates/voucher.html, field_crew.html, templates/field_crew.html, COLLABORATION.md
- **Objective**: Implement comprehensive real-time messaging support across WhatsApp Business API and National Telecom SMS gateways, connecting civic stakeholders (PWD Contractors, Ward Executive Engineers, Citizens, and Fleet Bus Drivers) directly to automated road hazard alerts and work orders.
- **Key Deliverables**:
  1. **Backend REST Endpoint (POST /api/send-alert)**: Validates phone numbers and delivery channels (WHATSAPP, SMS), routes through simulated Meta Cloud API / National DLT Gateways, and injects audit logs into the multi-agent telemetry stream.
  2. **Command Center Municipal Dispatch Modal**: Integrated into PWD Work Orders table with recipient role toggles (Contractor, Engineer, Citizen, Driver), live phone validator, auto-generated Markdown payload preview, and single-click WhatsApp/SMS triggers.
  3. **Citizen Portal Interactive Subscription & Mobile Input Normalization**: High-contrast input with `🇮🇳 +91` country code badge, auto-formatting, E.164 validation, live simulated message bubble preview (`✓ WhatsApp Cloud API` / `✓ Telecom DLT Gateway`), and deep action links to WhatsApp Web and native mobile SMS.
  4. **Instant Municipal Milestone Alerts**: Subscribed citizens receive automated instant WhatsApp & SMS notifications when the rapid response field crew arrives on-site (`IN_PROGRESS`) and when the repair is completed & verified (`RESOLVED`), synced via Web Audio API, `BroadcastChannel`, and background polling.
  5. **CPWD Tender Voucher Sharing**: Quick-action ribbon buttons ("WhatsApp Voucher", "SMS Voucher") to deliver formal procurement estimates with CPWD SOR codes directly to contractors.
  6. **Mobile Field Crew PWA Dispatch**: Quick status reporting buttons ("WhatsApp Engr", "SMS Update") with automated alerts triggered upon starting and resolving repairs.
  7. **100% Unit Test Pass Rate**: 32/32 unit tests passing, synced across main and gh-pages.

---

### 🟢 TASK-14: People & Inclusion — Multilingual Voice HUD, Route Ride-Quality Index, and Adopt-a-Road Citizen Rewards [COMPLETED]
- **Assignee**: Lead Inclusion & Human-Centered Civic Systems Engineer (Antigravity)
- **Target Files**: `backend/main.py`, `tests/test_pipeline.py`, `driver_console.html`, `templates/driver_console.html`, `analytics.html`, `templates/analytics.html`, `citizen_portal.html`, `templates/citizen_portal.html`, `COLLABORATION.md`
- **Objective**: Implement inclusive human-centered features across language accessibility (Kannada and Hindi in-cab voice synthesizers for drivers), bus fleet ride-quality smoothness scores using phone/IMU accelerometer data to schedule depot maintenance, and an anti-spam verified Adopt-a-Road citizen rewards marketplace.
- **Key Deliverables**:
  1. **Kannada & Hindi In-Cab Driver Voice Synthesizer**: Web Speech API TTS engine with voice language switcher (ಕನ್ನಡ, हिन्दी, English). Generates natural distance-calibrated spoken hazard alerts (e.g. "ಮುಂದೆ 100 ಮೀಟರ್‌ನಲ್ಲಿ ಗುಂಡಿ ಇದೆ. ಎಚ್ಚರ! ಎಡ ಪಥಕ್ಕೆ ಚಲಿಸಿ.", "आगे 100 मीटर पर गहरा गड्ढा है। कृपया गति धीमी करें।") with active audio waveform visualizer and manual replay button.
  2. **Phone/IMU Accelerometer Route Ride-Quality Index**: Calculates vertical Z-axis shock (g), RMS vibration (g), and International Roughness Index (IRI m/km) across transit routes (Mysuru Route 119, Bengaluru ORR 500D, Electronic City Elevated Tollway). Surfaces fleet maintenance wear rates (+XX% suspension wear) to help KSRTC and BMTC depot engineers schedule timely shock absorber maintenance before mechanical failure.
  3. **Adopt-a-Road Citizen Rewards Program (Zero-Spam Guard)**: Citizen reward club with verified points ledger, tier badges, and neighborhood street adoption (1.5x multiplier). Guarantees zero spam by awarding points ONLY when independent bus dashcams or DBSCAN fleet sweeps confirm the defect. Includes instant municipal perks marketplace (KSRTC/BMTC bus pass ₹250 discount, MCC property tax rebates, pool passes, and EV charging credits) with verifiable QR code certificates.
  4. **Backend REST APIs**: Endpoints `GET /api/driver-advisories/voice`, `GET /api/routes/ride-quality`, `GET /api/citizen-rewards`, and `POST /api/redeem-reward`.
  5. **100% Test Coverage**: 35/35 unit tests passing, synced across main and gh-pages.

---

### 🟢 TASK-15: Real-Time Live Camera Video Analyzer & Automated Driving Directions [COMPLETED]
- **Assignee**: Lead Computer Vision & Autonomous Navigation Systems Architect (Antigravity)
- **Target Files**: `backend/main.py`, `tests/test_pipeline.py`, `index.html`, `templates/index.html`, `static/js/app.js`, `driver_console.html`, `templates/driver_console.html`, `COLLABORATION.md`
- **Objective**: Implement real-time hardware camera ingestion (webcam / mobile phone camera) for continuous live video analysis, overlaying real-time YOLO defect bounding boxes, and generating turn-by-turn navigation directions, visual driving maneuvers, spoken voice guidance (Kannada, Hindi, English), and field crew depot dispatch routes.
- **Key Deliverables**:
  1. **Hardware Camera Ingestion (`getUserMedia`)**: Direct video stream from front/rear phone cameras and PC webcams rendered in 60 FPS canvas with flip camera toggle and zero disk latency.
  2. **Real-Time Driving Maneuvers & Direction HUD**: Live directional arrows and maneuvers (e.g. `↖ Merge Left Lane in 25m to Avoid Crater`, `⬇ Reduce Speed to 15 km/h for Waterlogging`, `⬆ Maintain Center Lane`).
  3. **Turn-by-Turn Detour Navigation**: 3-step detour routing around detected distress zones to protect vehicle suspensions and prevent bottleneck gridlock.
  4. **One-Click Navigation Links**: Instant launch into Google Maps turn-by-turn navigation (`https://www.google.com/maps/dir/?api=1&destination=lat,lng`) and interactive PWD Rapid Response Van Depot Route modal.
  5. **Multilingual Voice Navigation Prompts**: Spoken driving maneuvers in Kannada, Hindi, and English.
  6. **100% Test Coverage**: 36/36 unit tests passing, synced across main and gh-pages.


---

### 🟢 TASK-16: Official Government & GIGW 3.0 Compliance, MCC e-Procurement Tenders, 24x7 Helplines & 9 Zonal Offices Directory, Janahitha 48-Hour SLA Tracker, and Verifiable Road Safety Inspection Certificates [COMPLETED]
- **Assignee**: Lead Civic Governance & Public Digital Systems Architect (Antigravity)
- **Target Files**: `backend/main.py`, `tests/test_pipeline.py`, `index.html`, `templates/index.html`, `static/js/app.js`, `citizen_portal.html`, `COLLABORATION.md`
- **Objective**: Transform UrbanSight AI into an authentic, production-grade official Municipal Corporation & Smart Cities Mission portal complying with Guidelines for Indian Government Websites (GIGW 3.0), Karnataka Transparency in Public Procurements (KTPP) Act 1999, Right to Information (RTI) Act 2005 §4(1)(b), and Karnataka Sakala Services Act 2011.
- **Key Deliverables**:
  1. **GIGW 3.0 Official Government Masthead & Accessibility Controls**:
     - Dual-language State emblem & title banner: `ಕರ್ನಾಟಕ ಸರ್ಕಾರ · ಮೈಸೂರು ಮಹಾನಗರ ಪಾಲಿಕೆ | Government of Karnataka · Mysuru City Corporation (MCC)`.
     - Smart Cities Mission, PM GatiShakti, and Digital India national badges.
     - Interactive font size adjuster (`A-`, `A`, `A+`) dynamically scaling DOM typography via CSS variables.
     - High Contrast toggle (`body.high-contrast`) complying with WCAG 2.1 AA accessibility guidelines.
     - Language switcher (English, ಕನ್ನಡ, हिन्दी) and GIGW 3.0 screen reader tags.
     - National Tricolor ribbon (`#FF9933` Saffron, `#FFFFFF` White, `#138808` Green).
  2. **Live Public Notice Board & Monsoon Road Advisory Marquee**:
     - Dynamic rolling marquee ticker broadcasting real-time civic road work notices, transit route 119 diversions, monsoon standby vans, and citizen rewards schemes with pause/play and full notices modal.
  3. **MCC e-Procurement Active Tenders & Public Transparency Board (KTPP Act 1999)**:
     - Real-time road resurfacing and drainage tender listings across Mysuru (Hunsur Road, Sayyaji Rao Road, Outer Ring Road, Saraswathipuram) with Tender IDs, contractor names, SLA reliability ratings (89.8% to 96.0%), and Defect Liability Periods (DLP).
     - Ward budget allocation summary (₹14.80 Cr sanctioned, ₹9.42 Cr utilized across 65 wards).
     - Proactive public audit disclosure under RTI Act Section 4(1)(b).
  4. **24x7 Emergency Helplines & 9 Zonal Offices Directory**:
     - Direct dial cards: MCC Toll-Free `1800-425-4766`, Control Room `0821-2418800`, Mysore City Traffic Police `1095` / WhatsApp `+91 94808 02200`, Fire & Rescue `101`, and KSRTC breakdown assistance.
     - Searchable directory of all 9 Mysuru City Corporation Zonal Offices with Assistant Executive Engineer (AEE) and Junior Engineer (JE) contact numbers.
  5. **Janahitha 48-Hour Citizen Charter SLA Status Tracker**:
     - Instant ticket lookup with live 48-hour resolution countdown timer (`29 hrs 30 mins remaining · WITHIN GUARANTEED SLA`).
     - 6-Stage resolution milestone tracker.
     - Formal statutory escalation trigger to the Zonal Commissioner under Karnataka Sakala Services Act 2011.
  6. **Downloadable / Printable Official Road Safety Inspection Certificate**:
     - Official Government Certificate layout with State seal, certificate number (`MCC/PWD/RSI-2026/0941`), and Indian Roads Congress (IRC:SP:20) compliance badge.
     - Marshall density test results (98.4%), pre/post PCI ratings (41.2 to 96.5), geo-tagged before/after photos, verification QR code, and digital signature of Assistant Executive Engineer (Roads). Includes `@media print` styling for A4 export.
  7. **Official Government Footer**:
     - Web Information Manager (WIM) nodal contact, KSDC / NIC cloud hosting tag, DPDP Act 2023 privacy notice, and live civic telemetry counter (412 km monitored, 1,482 grievances resolved).
  8. **100% Test Coverage**: 42/42 unit tests passing, synced across main and gh-pages.


---

### 🟢 TASK-17: Clean OpenStreetMap Integration (Zero Watermarks) & Real-Time Visual Turn-by-Turn Driving Directions on Map [COMPLETED]
- **Assignee**: Lead Geospatial GIS & Autonomous Navigation Architect (Antigravity)
- **Target Files**: `index.html`, `templates/index.html`, `static/js/app.js`, `COLLABORATION.md`
- **Objective**: Fix third-party Carto tilelayer watermark prompt ("API KEY REQUIRED carto.com/basemaps/apikey") by integrating high-resolution, key-free OpenStreetMap standard tiles, and actively render interactive visual driving directions, detour route polylines, waypoint badges, and a floating turn-by-turn navigation HUD directly on the Leaflet GIS canvas.
- **Key Deliverables**:
  1. **Clean OpenStreetMap Standard Basemap**: Replaced Carto Voyager tile endpoint with `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`. Zero API keys, zero watermarks, sharp street names, and landmark detail across Mysuru and Karnataka.
  2. **Active Direction Route Polyline Rendering (`drawMapDirectionRoute()`)**:
     - High-contrast white casing (`weight: 9, opacity: 0.95`).
     - Vibrant cyan sapphire navigation polyline (`#0284C7`, `weight: 5`).
     - Animated marching dashed pulse overlay (`#38BDF8`, `weight: 3, dashArray: '8, 12'`).
  3. **Custom Waypoint Badges**: High-contrast interactive badges placed on the map: `🚩 Start: KSRTC Bus KA09-E102`, `⚠️ Pothole Ahead (Merge Left in 25m)`, `↪️ Detour Bypass: Temple Road`, and `🏁 Clear Corridor Rejoin`.
  4. **Floating Map Driving Directions HUD (`#map-directions-hud`)**:
     - Live maneuver banner (`↖ MERGE LEFT IN 25m`).
     - 4-Step turn guidance scroller with highlight indicators.
     - Telemetry strip (Distance: 1.8 km | ETA: 4 mins | Speed: 38 km/h).
     - Action buttons: Spoken Voice Alert (`🔊` in Kannada, Hindi, and English), Route Mode toggle (`🚗 Vehicle Detour` vs `🚜 PWD Depot Crew Route`), and one-click Google Maps Navigation (`🗺️`).
  5. **Dynamic Route Recalculation**: Clicking any Mysuru landmark (`🏫 VVCE Gokulam`, `🚦 Hunsur Rd Signal`, `🏥 Columbia Asia`, `🏞️ Chamundi Foothills`, `💻 Infosys Campus`) or hazard automatically redraws the driving direction route to that site!
  6. **100% Test Coverage**: 42/42 unit tests passing, synced across main and gh-pages.

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
- [x] TASK-11: Mysuru GIS Map Integration & Realistic Civic Iconography (All portals, maps & backend) — Lead Frontend UI/UX Architect (Completed)
- [x] TASK-12: Transit Video & Photo Road Inspection AI Analyzer Engine (Backend, Frontend, Tests) — Lead Vision & Fullstack Engineer (Completed)
- [x] TASK-13: Automated WhatsApp & SMS Municipal Alert Notification Gateway (Backend, Frontend, Tests) — Lead Messaging & Fullstack Systems Engineer (Completed)
- [x] TASK-14: People & Inclusion — Multilingual Voice HUD, Route Ride-Quality Index, and Adopt-a-Road Citizen Rewards (Backend, Frontend, Tests) — Lead Inclusion & Human-Centered Civic Systems Engineer (Completed)
- [x] TASK-15: Real-Time Live Camera Video Analyzer & Automated Driving Directions (Backend, Frontend, Tests) — Lead Computer Vision & Autonomous Navigation Systems Architect (Completed)

- [x] TASK-16: Official Government & GIGW 3.0 Compliance, MCC e-Procurement Tenders, 24x7 Helplines & 9 Zonal Offices Directory, Janahitha 48-Hour SLA Tracker, and Verifiable Road Safety Inspection Certificates (Backend, Frontend, Tests) — Lead Civic Governance & Public Digital Systems Architect (Completed)
- [x] TASK-17: Clean OpenStreetMap Integration (Zero Watermarks) & Real-Time Visual Turn-by-Turn Driving Directions on Map (Frontend, GIS Leaflet, Tests) — Lead Geospatial GIS & Autonomous Navigation Architect (Completed)