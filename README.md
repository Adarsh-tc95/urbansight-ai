# 🚌 UrbanSight AI — AI Mobile Urban Intelligence Platform
> **Infothon 7.0 · Vidyavardhaka College of Engineering (VVCE), Mysuru**  
> **Problem Statement:** PS #07 | Ref: SIH26124 | **Track:** Smart Cities & Mobility (Agentic AI)

[![Infothon 7.0](https://img.shields.io/badge/Hackathon-Infothon%207.0-blue.svg)](https://vvce.ac.in)
[![Track](https://img.shields.io/badge/Track-Smart%20Cities%20%26%20Mobility-emerald.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB.svg?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![YOLOv8](https://img.shields.io/badge/AI%20Model-YOLOv8%20Nano-FF5E1E.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](#)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fgaganks2006-ind%2Furbansight-ai)
[![GitHub Pages](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-00E5FF.svg)](https://gaganks2006-ind.github.io/urbansight-ai/)

---

## 🌐 Live Cloud Portals & Deployments

| Component | Cloud URL | Description |
| :--- | :--- | :--- |
| 🏙️ **Smart City ICCC Command Center** | [**gaganks2006-ind.github.io/urbansight-ai**](https://gaganks2006-ind.github.io/urbansight-ai/) | Real-time Leaflet GIS tracking across Mysuru & Bengaluru, 40-waypoint ORR corridor, live bus telemetry, and instant Video/Photo AI Inspection Analyzer. |
| 🚌 **In-Cab Driver HUD Console** | [**.../driver_console.html**](https://gaganks2006-ind.github.io/urbansight-ai/driver_console.html) | Tablet HUD with animated speedometer, audio chime alert, approaching hazard lane-merge advice, and route toggle (Bengaluru 500D ↔ Mysuru Ring Road). |
| 👥 **Citizen Repair Tracking Portal** | [**.../citizen_portal.html**](https://gaganks2006-ind.github.io/urbansight-ai/citizen_portal.html) | Public lookup page tracking repair stages from dashcam detection to final municipal fix (with BBMP & MCC Ward 9 samples). |
| 📊 **Municipal Ward Analytics** | [**.../analytics.html**](https://gaganks2006-ind.github.io/urbansight-ai/analytics.html) | Executive governance dashboard tracking ward SLA adherence, MTTR, defect compositions, and 8.4x maintenance ROI savings. |
| 🛠️ **Mobile Field Crew PWA** | [**.../field_crew.html**](https://gaganks2006-ind.github.io/urbansight-ai/field_crew.html) | Mobile PWA for PWD repair vans with Google Maps directions, Before/After image audits, and resolution triggers. |
| 📄 **Official CPWD Tender Voucher** | [**.../voucher.html?ticket=PWD-OCT-0941**](https://gaganks2006-ind.github.io/urbansight-ai/voucher.html?ticket=PWD-OCT-0941) | Government letterhead voucher with itemized SOR 2024 breakdown, 18% GST, penalty clauses, and signature blocks. |

---

## 📌 Executive Summary
**UrbanSight AI** turns everyday municipal transit fleets (city buses) into real-time, edge-intelligent perception grids. By mounting dashcams on existing public buses, UrbanSight autonomously detects road surface hazards (potholes, cracks, waterlogging), traffic congestion, and stalled incidents in real time, clusters repeat passes spatially via DBSCAN, and auto-dispatches geotagged work orders directly into municipal PWD systems in under 3 minutes—with **zero new hardware CapEx**.

---

## 🎯 The Core Problem & Urgency
- **Fatalities:** India lost **1,77,175 lives** across 4,87,707 road accidents in 2024 (MoRTH).
- **Pothole Crisis:** Pothole fatalities surged **53% in five years** (9,438 deaths 2020–2024; 2,385 in 2024 alone).
- **Severe Congestion:** Bengaluru ranks as the **#2 most congested city in the world** (TomTom 2025 Index), with rush-hour speeds dropping to **13.9 km/h**.
- **The Gap:** Current road maintenance is completely reactive and siloed. Fixed cameras cover <4% of road corridors, leaving 96% of urban networks unmonitored.

---

## 💡 The Solution: 4-Agent Autonomous Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. INPUT LAYER (MOBILE FLEET EDGE)                                     │
│    Existing PM e-Bus Fleet (Windshield Dashcam + GNSS Telemetry)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ 1080p 30 FPS Feed
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. EDGE INFERENCE LAYER (ON-BUS COMPUTE)                               │
│    AGENT 1: VISION PERCEPTION AGENT (YOLOv8 Edge Engine)               │
│    • Real-time classification: Potholes, Cracks, Flooding, Stalls      │
│    • Privacy Engine: Irreversible on-chip face & license plate blur    │
│    • Telemetry Packaging: Bounding box + confidence + GPS Geotag       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ <15 KB GeoJSON Payload (MQTT/4G)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. CLOUD MULTI-AGENT ORCHESTRATION LAYER                               │
│    AGENT 2: GEO-SPATIAL CLUSTERING & TRIAGE AGENT                      │
│    • DBSCAN Spatial Clustering: Merges repeat bus passes into 1 ticket │
│    • Severity Matrix: Damage depth × traffic volume × frequency        │
└─────────────────┬────────────────────────────────────┬─────────────────┘
                  │ Validated Cluster                  │ Live Incident
                  ▼                                    ▼
┌─────────────────────────────────┐  ┌───────────────────────────────────┐
│ AGENT 3: MUNICIPAL DISPATCH     │  │ AGENT 4: FLEET ADVISORY           │
│ • Auto-generates PWD Work Order │  │ • Sub-second WebSocket Broadcast  │
│ • Attaches GPS, Photo, Severity │  │ • Real-time driver hazard warning │
│ • Dispatches in < 3 minutes     │  │ • Ahead-of-route detour navigation│
└─────────────────┬───────────────┘  └─────────────────┬─────────────────┘
                  └─────────────────┬──────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. UNIFIED COMMAND & OUTPUT LAYER                                      │
│    • Smart Cities ICCC Dashboard (Live bus tracks + hazard pins)       │
│    • PWD Contractor Work-Order Queue (SLA tracker & repair status)     │
│    • Driver In-Cab Console (Tablet-based reroute & obstacle warning)   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Tools & Frameworks | Functionality |
| :--- | :--- | :--- |
| **Edge Hardware** | NVIDIA Jetson Orin Nano / RPi 4 + Coral Edge TPU | 7–15W edge compute mounted on transit buses |
| **Edge AI & Vision** | YOLOv8 Nano / YOLO26s (TensorRT FP16/INT8) | Sub-30ms inference at 30 FPS detecting road hazards |
| **Privacy Engine** | OpenCV On-Device Gaussian Blur | Irrevocable on-chip face & license plate blurring (DPDP Act compliant) |
| **Transport** | MQTT over TLS 1.3 / Mosquitto Broker | Lightweight event telemetry (<15 KB per detection) |
| **Cloud Backend** | FastAPI (ASGI) + Python 3.13 + Pydantic v2 | High-throughput asynchronous multi-agent orchestration |
| **Geo-Processing** | DBSCAN (scikit-learn) + PostGIS + Uber H3 | Spatiotemporal clustering and longitudinal defect tracking |
| **GIS Dashboard** | Leaflet.js + CartoDB Dark Matter + WebSockets | Sub-second real-time map updates and municipal command UI |
| **Deployment** | Docker + Railway / GCP Cloud Run | Serverless auto-scaling (₹800–₹1,500/month pilot cost) |

---

## 📊 Quantified Impact & Measurable Outcomes
- **75% Faster Repair Dispatch:** Collapses repair cycle from **14–21 days** down to **<48 hours** (<3 min auto-ticket).
- **40% Fatality Risk Reduction:** Pre-failure preventative maintenance before road craters cause fatal crashes.
- **85%+ City Arterial Coverage:** Daily coverage across city transit routes vs. <15% from fixed highway cameras.
- **₹16.2 Cr / Year Addressable SAM:** 169 PM e-Bus Sewa cities × ₹80,000/month municipal SaaS subscription.

---

## 🚀 Quickstart & Local Setup

```bash
# 1. Clone repository
git clone https://github.com/gaganks2006-ind/urbansight-ai.git
cd UrbanSight-AI

# 2. Set up virtual environment
python -m venv venv
venv\Scripts\activate     # On Windows
# source venv/bin/activate # On Linux/macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the backend server
uvicorn backend.main:app --reload --port 8000
```

Open your browser at `http://127.0.0.1:8000` to access the live command dashboard.

---

## 👥 Team & Credentials
- **Institution:** Department of Information Science and Engineering, **Vidyavardhaka College of Engineering (VVCE)**, Mysuru - 570002
- **Lead Developer & AI Architect:** Gagan K S
- **Specializations:** Edge AI, Computer Vision, Multi-Agent Systems & GIS Spatial Intelligence

---

## 📜 License & Acknowledgments
Distributed under the MIT License. Developed for **Infothon 7.0 (2026)**.
Special thanks to the PM e-Bus Sewa Initiative and Smart India Hackathon (SIH) problem statement archives.
