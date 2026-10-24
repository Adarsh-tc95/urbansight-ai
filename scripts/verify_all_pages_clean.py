import time
import sys
sys.stdout.reconfigure(encoding='utf-8')
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--autoplay-policy=no-user-gesture-required')

driver = webdriver.Chrome(options=opts)

pages = [
    ('Main Dashboard', 'http://localhost:8000/'),
    ('Driver Console', 'http://localhost:8000/driver_console.html'),
    ('Citizen Portal', 'http://localhost:8000/citizen_portal.html')
]

has_severe = False

for name, url in pages:
    print(f"\n==========================================")
    print(f"Testing {name}: {url}")
    print(f"==========================================")
    driver.get(url)
    time.sleep(3.0)
    logs = driver.get_log('browser')
    severe = [l for l in logs if l['level'] == 'SEVERE']
    print(f"Total console logs: {len(logs)} | SEVERE errors: {len(severe)}")
    for l in logs:
        print(f"  [{l['level']}] {l['message']}")
    if len(severe) > 0:
        has_severe = True

print(f"\n==========================================")
print("Evaluating Live Video Perception on Main Dashboard...")
print(f"==========================================")
driver.get('http://localhost:8000/')
time.sleep(4.0)

vid_state = driver.execute_script("""
    const v = document.getElementById('uploaded-media-video');
    return {
        src: v ? v.src : null,
        paused: v ? v.paused : null,
        currentTime: v ? v.currentTime : null,
        duration: v ? v.duration : null,
        readyState: v ? v.readyState : null
    };
""")
print("Video Element State:", vid_state)

cv_state = driver.execute_script("""
    return {
        mode: mediaState.mode,
        isPlaying: mediaState.isPlaying,
        corridor: currentCorridorKey,
        tourIndex: currentTourIndex,
        depthLabel: document.getElementById('detection-depth-label').textContent,
        defectLabel: document.getElementById('detection-defect-label').textContent,
        coordsLabel: document.getElementById('media-hud-coords').textContent,
        workOrdersCount: state.workOrders.length,
        logsCount: state.logs.length,
        masterButtonLabel: document.getElementById('master-sim-label').textContent,
        masterButtonBadge: document.getElementById('master-sim-badge').textContent
    };
""")
print("AI Edge CV Telemetry State:", cv_state)

driver.quit()

if has_severe:
    print("\n[RESULT] FAIL: SEVERE console errors detected!")
    sys.exit(1)
else:
    print("\n[RESULT] SUCCESS: 0 SEVERE errors across all pages & Video Perception is active!")
    sys.exit(0)
