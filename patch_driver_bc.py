import os

path = os.path.join("Infothon 7.0", "templates", "driver_console.html")
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

target = "setInterval(pollTelemetryAPI, 2000);\n        pollTelemetryAPI();"
replacement = """setInterval(pollTelemetryAPI, 2000);
        pollTelemetryAPI();

        // Cross-Tab Listener for Real-Time AI Hazards Dispatched from Command Center
        try {
            const driverChannel = new BroadcastChannel('urbansight_crew_events');
            driverChannel.onmessage = (e) => {
                if (e.data && e.data.event_type === 'NEW_DEFECT_DISPATCHED') {
                    setHazardAlert(
                        `${e.data.hazard_type || 'POTHOLE'} DETECTED`,
                        e.data.location_name || "Ahead on Bus Path (180m Horizon)",
                        180,
                        "MERGE LEFT LANE & REDUCE SPEED TO 20 KM/H",
                        "Live Edge Detection Dispatched by ICCC Master Agent",
                        2,
                        -0.40
                    );
                    playVoiceAdvisory("Kannada");
                }
            };
        } catch (err) {}"""

if target in text:
    text = text.replace(target, replacement, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    with open(os.path.join("Infothon 7.0", "driver_console.html"), "w", encoding="utf-8") as f:
        f.write(text)
    print("PATCHED_DRIVER_CONSOLE_SUCCESS")
else:
    print("TARGET_NOT_MATCHED_IN_DRIVER")
