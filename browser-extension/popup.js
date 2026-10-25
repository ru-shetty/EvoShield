const stateEl = document.querySelector('#state');
const toggleButton = document.querySelector('#toggle');
const riskEl = document.querySelector('#risk');

function render(values) {
  const enabled = values.auto_check_enabled !== false;
  stateEl.textContent = enabled
    ? 'Automatic website address checks are on.'
    : 'Automatic website address checks are paused.';
  stateEl.className = `state ${enabled ? 'on' : 'off'}`;
  toggleButton.textContent = enabled ? 'Pause automatic checks' : 'Enable automatic checks';
  toggleButton.className = `button ${enabled ? '' : 'off'}`;

  const result = values.last_check;
  if (!result) return;
  riskEl.textContent = result.risk || 'Check complete';
  riskEl.className = `risk ${result.verdict === 'HIGH' ? 'high' : ['MEDIUM', 'REVIEW'].includes(result.verdict) ? 'medium' : result.verdict === 'LOW' ? 'low' : ''}`;
  document.querySelector('#host').textContent = result.host || '';
  document.querySelector('#message').textContent = result.message || '';
  document.querySelector('#time').textContent = result.checked_at
    ? `Checked ${new Date(result.checked_at).toLocaleString()}`
    : '';
}

async function refresh() {
  render(await chrome.storage.local.get({ auto_check_enabled: true, last_check: null }));
}

toggleButton.addEventListener('click', async () => {
  const values = await chrome.storage.local.get({ auto_check_enabled: true });
  const enabled = values.auto_check_enabled === false;
  await chrome.storage.local.set({ auto_check_enabled: enabled });
  if (enabled) chrome.runtime.sendMessage({ type: 'scan_open_tabs' });
  await refresh();
});

chrome.storage.onChanged.addListener(() => void refresh());
void refresh();
