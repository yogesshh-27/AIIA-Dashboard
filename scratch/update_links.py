with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Make sidebar links use onclick="switchStaffTab('...'); return false;"
for tab in ['dashboard', 'active-trials', 'sites', 'trial-info', 'approvals', 'gcp', 'doctors', 'patients', 'pv', 'reports', 'interop']:
    old_link = f'onclick="switchStaffTab(\'{tab}\')"'
    new_link = f'onclick="switchStaffTab(\'{tab}\'); return false;"'
    html = html.replace(old_link, new_link)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("index.html updated with smooth link handling.")
