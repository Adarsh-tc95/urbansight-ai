import sys

def fix_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Guard in renderHazardsOnMap
    old_marker = 'L.marker([h.lat, h.lng], { icon: hazardIcon })'
    new_marker = 'if (typeof h.lat !== "number" || isNaN(h.lat) || typeof h.lng !== "number" || isNaN(h.lng)) return;\n                L.marker([h.lat, h.lng], { icon: hazardIcon })'
    if old_marker in content and 'typeof h.lat !== "number"' not in content:
        content = content.replace(old_marker, new_marker, 1)
        print(f"Guarded marker in {filename}")

    # 2. Guard in runAIAnalysisAndDispatch
    old_fly = 'state.map.flyTo([d.lat, d.lng], 15, { duration: 1.2 });'
    new_fly = 'if (typeof d.lat === "number" && typeof d.lng === "number" && !isNaN(d.lat) && !isNaN(d.lng)) { state.map.flyTo([d.lat, d.lng], 15, { duration: 1.2 }); }'
    if old_fly in content:
        content = content.replace(old_fly, new_fly, 1)
        print(f"Guarded flyTo in {filename}")

    # 3. Guard d.lat & d.lng initialization in runAIAnalysisAndDispatch
    old_dispatch_init = """function runAIAnalysisAndDispatch(targetPothole) {
            const d = mediaState.defect;
            if (targetPothole) {
                d.lat = targetPothole.lat || d.lat;
                d.lng = targetPothole.lng || d.lng;"""
    new_dispatch_init = """function runAIAnalysisAndDispatch(targetPothole) {
            const d = mediaState.defect;
            const corr = (CORRIDORS && CORRIDORS[currentCorridorKey]) ? CORRIDORS[currentCorridorKey] : (CORRIDORS && CORRIDORS['mysuru-orr'] ? CORRIDORS['mysuru-orr'] : {});
            let safeLat = (targetPothole && typeof targetPothole.lat === 'number') ? targetPothole.lat : ((d && typeof d.lat === 'number') ? d.lat : 12.3360);
            let safeLng = (targetPothole && typeof targetPothole.lng === 'number') ? targetPothole.lng : ((d && typeof d.lng === 'number') ? d.lng : 76.6210);
            d.lat = safeLat;
            d.lng = safeLng;
            if (targetPothole) {
                d.lat = safeLat;
                d.lng = safeLng;"""
    if old_dispatch_init in content:
        content = content.replace(old_dispatch_init, new_dispatch_init, 1)
        print(f"Guarded runAIAnalysisAndDispatch in {filename}")

    # 4. Guard matchedPothole & defP in drawLoop
    old_loop_detect = """            if (matchedPothole) {
                mediaState.detectedPotholeIds.add(matchedPothole.id);
                mediaState.activePothole = matchedPothole;
                dispatchContinuousDefect(matchedPothole);
            } else if (!mediaState.hasDispatchedOnce && (mediaState.frameCount >= 45 || (mediaState.userVideo && mediaState.userVideo.currentTime >= 1.2))) {
                mediaState.hasDispatchedOnce = true;
                const defP = (corr.potholes && corr.potholes[0]) || {
                    id: 'FP-MYS-1', progress: 0.12, xRatio: 0.42, yRatio: 0.62, width: 148, height: 62, depthCm: 11.4, name: `${corr.short} (Ch: 1.05 km), Mysuru`, ticketId: 'PWD-MYS-7141'
                };
                mediaState.detectedPotholeIds.add(defP.id);
                mediaState.activePothole = defP;
                dispatchContinuousDefect(defP);
            }"""

    new_loop_detect = """            if (matchedPothole) {
                if (typeof matchedPothole.lat !== 'number') {
                    const mProg = matchedPothole.progress || 0.35;
                    matchedPothole.lat = Number((corr.startLat + mProg * (corr.endLat - corr.startLat)).toFixed(4));
                    matchedPothole.lng = Number((corr.startLng + mProg * (corr.endLng - corr.startLng)).toFixed(4));
                }
                mediaState.detectedPotholeIds.add(matchedPothole.id);
                mediaState.activePothole = matchedPothole;
                dispatchContinuousDefect(matchedPothole);
            } else if (!mediaState.hasDispatchedOnce && (mediaState.frameCount >= 45 || (mediaState.userVideo && mediaState.userVideo.currentTime >= 1.2))) {
                mediaState.hasDispatchedOnce = true;
                const defP = (corr.potholes && corr.potholes[0]) || {
                    id: 'FP-MYS-1', progress: 0.12, xRatio: 0.42, yRatio: 0.62, width: 148, height: 62, depthCm: 11.4, name: `${corr.short} (Ch: 1.05 km), Mysuru`, ticketId: 'PWD-MYS-7141'
                };
                if (typeof defP.lat !== 'number') {
                    const dProg = defP.progress || 0.12;
                    defP.lat = Number((corr.startLat + dProg * (corr.endLat - corr.startLat)).toFixed(4));
                    defP.lng = Number((corr.startLng + dProg * (corr.endLng - corr.startLng)).toFixed(4));
                }
                mediaState.detectedPotholeIds.add(defP.id);
                mediaState.activePothole = defP;
                dispatchContinuousDefect(defP);
            }"""
    if old_loop_detect in content:
        content = content.replace(old_loop_detect, new_loop_detect, 1)
        print(f"Guarded loop detection in {filename}")

    with open(filename, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print(f"{filename} fully patched")

fix_file('index.html')
fix_file('templates/index.html')
