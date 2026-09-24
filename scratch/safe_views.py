import re

with open("app.js", "r", encoding="utf-8") as f:
    code = f.read()

# Replace renderPatientsView
old_pat = """async function renderPatientsView(container) {
  const res = await fetch('/api/ayur/patients');
  const data = await res.json();
  const patients = data.patients || [];"""

new_pat = """async function renderPatientsView(container) {
  try {
    const res = await fetch('/api/ayur/patients');
    const data = await res.json();
    const patients = data.patients || [];"""

if old_pat in code:
    # also add closing try-catch before the end of the function
    target_end = """        </tbody>
      </table>
    </div>
  `;
}"""
    replacement_end = """        </tbody>
      </table>
    </div>
  `;
  } catch (err) {
    console.error('Error rendering patients view:', err);
    container.innerHTML = `
      <div class="view-header-bar">
        <div class="view-title-group">
          <h2>Patient Management & Clinical Roster</h2>
          <p>Registered clinical trial participants under active protocol care</p>
        </div>
      </div>
      <div style="background: #ffffff; padding: 40px; border-radius: 8px; text-align: center; border: 1px solid var(--border-light);">
        <p style="color: var(--text-secondary); margin-bottom: 14px;">Error connecting to clinical database. Please check your network or click retry.</p>
        <button class="btn btn-primary btn-sm" onclick="switchStaffTab('patients')">🔄 Retry Loading Patients</button>
      </div>
    `;
  }
}"""
    code = code.replace(old_pat, new_pat)
    code = code.replace(target_end, replacement_end)
    print("Wrapped renderPatientsView in try-catch")

with open("app.js", "w", encoding="utf-8") as f:
    f.write(code)

print("app.js updated.")
