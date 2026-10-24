import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def update_links(content):
    # Mapping
    replacements = [
        (r'href=["\']index\.html["\']', 'href="index.html#command" onclick="if(window.top !== window && window.top.switchDashboardTab){ window.top.switchDashboardTab(\'command\', event); return false; }"'),
        (r'href=["\']driver_console\.html["\']', 'href="index.html#driver" onclick="if(window.top !== window && window.top.switchDashboardTab){ window.top.switchDashboardTab(\'driver\', event); return false; }"'),
        (r'href=["\']citizen_portal\.html["\']', 'href="index.html#citizen" onclick="if(window.top !== window && window.top.switchDashboardTab){ window.top.switchDashboardTab(\'citizen\', event); return false; }"'),
        (r'href=["\']field_crew\.html["\']', 'href="index.html#crew" onclick="if(window.top !== window && window.top.switchDashboardTab){ window.top.switchDashboardTab(\'crew\', event); return false; }"'),
        (r'href=["\']analytics\.html["\']', 'href="index.html#analytics" onclick="if(window.top !== window && window.top.switchDashboardTab){ window.top.switchDashboardTab(\'analytics\', event); return false; }"'),
        (r'href=["\']voucher\.html\?ticket=[^"\']*["\']', 'href="index.html#voucher" onclick="if(window.top !== window && window.top.switchDashboardTab){ window.top.switchDashboardTab(\'voucher\', event); return false; }"'),
        (r'href=["\']voucher\.html["\']', 'href="index.html#voucher" onclick="if(window.top !== window && window.top.switchDashboardTab){ window.top.switchDashboardTab(\'voucher\', event); return false; }"')
    ]
    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)
    return content

files_to_update = [
    'driver_console.html',
    'citizen_portal.html',
    'field_crew.html',
    'analytics.html',
    'voucher.html',
    'templates/driver_console.html',
    'templates/citizen_portal.html',
    'templates/field_crew.html',
    'templates/analytics.html',
    'templates/voucher.html'
]

for rel_path in files_to_update:
    full_path = os.path.join(BASE_DIR, rel_path)
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            c = f.read()
        updated_c = update_links(c)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(updated_c)
        print(f"Updated links in {rel_path}")

print("All subpage navigation links synced to unified SPA parent router!")
