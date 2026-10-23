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
2. **Test Before Pushing**: Always verify `python -m unittest tests/test_pipeline.py` returns 21/21 passed (100%) before committing.
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

## 🔄 Status Tracker
- [x] Backend 4-Agent Modular Architecture (`tests/test_pipeline.py` 21/21 passing) — Node A
- [x] Real-time GIS Command Dashboard (`index.html`) — Node A
- [x] OGC GeoJSON Export (`/api/export-geojson`) — Node A
- [x] TASK-01: In-Cab Driver HUD Console UI (`driver_console.html`, `templates/driver_console.html`) — Node B (Completed)
- [x] TASK-02: Multi-Route Karnataka GPS Telemetry (`distributed/routes/*.json`) — Node B (Completed)
- [x] TASK-03: Edge Hardware & AI Model Benchmark Suite (`distributed/edge_benchmark.py`, `BENCHMARK_RESULTS.md`) — Node B (Completed)
- [x] TASK-04: Public Citizen Repair Tracking Portal (`citizen_portal.html`, `templates/citizen_portal.html`) — Node B (Completed)
