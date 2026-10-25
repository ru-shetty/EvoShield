const API = 'http://127.0.0.1:8000/api/v1/scan/';
const lastSent = new Map();

function safePageAddress(raw) {
  try {
    const url = new URL(raw);
    if (!['http:', 'https:'].includes(url.protocol)) return null;
    // Query strings and fragments can contain session tokens or personal data.
    url.search = '';
    url.hash = '';
    return url.toString();
  } catch {
    return null;
  }
}

chrome.runtime.onInstalled.addListener(async () => {
  const values = await chrome.storage.local.get('auto_check_enabled');
  if (typeof values.auto_check_enabled !== 'boolean') {
    await chrome.storage.local.set({ auto_check_enabled: true });
  }
  await scanOpenTabs();
});

chrome.runtime.onStartup.addListener(() => void scanOpenTabs());

chrome.tabs.onUpdated.addListener((tabId, change, tab) => {
  if (change.status === 'complete' && tab.url) void checkPage(tabId, tab.url);
});

chrome.runtime.onMessage.addListener(message => {
  if (message?.type !== 'scan_open_tabs') return;
  void scanOpenTabs(true);
});

async function scanOpenTabs(force = false) {
  if (force) lastSent.clear();
  const settings = await chrome.storage.local.get({ auto_check_enabled: true });
  if (!settings.auto_check_enabled) return;
  chrome.tabs.query({}, tabs => {
    for (const tab of tabs) {
      if (Number.isInteger(tab.id) && tab.url) void checkPage(tab.id, tab.url);
    }
  });
}

async function checkPage(tabId, rawUrl) {
  const settings = await chrome.storage.local.get({ auto_check_enabled: true });
  if (!settings.auto_check_enabled) return;
  const address = safePageAddress(rawUrl);
  if (!address || lastSent.get(tabId) === address) return;
  lastSent.set(tabId, address);

  try {
    const response = await fetch(API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: 'url', source: 'browser-extension', content: address, subject: address })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `EvoShield returned ${response.status}`);

    const verdict = data.verdict || 'LOW';
    const risk = verdict === 'HIGH' ? 'High risk' : ['MEDIUM', 'REVIEW'].includes(verdict) ? 'Suspicious' : 'Lower risk';
    const host = new URL(address).hostname;
    const result = {
      enabled: true,
      checked_at: new Date().toISOString(),
      host,
      url: address,
      risk,
      verdict,
      message: verdict === 'HIGH'
        ? 'This website address has strong warning signs. Avoid entering passwords, codes, or payment details.'
        : ['MEDIUM', 'REVIEW'].includes(verdict)
          ? 'This website address has warning signs. Use caution before entering information.'
          : 'No strong warning signs were found in the address. This does not prove the website is safe.'
    };
    await chrome.storage.local.set({ last_check: result });
    if (verdict === 'HIGH') {
      await chrome.action.setBadgeBackgroundColor({ tabId, color: '#d83b4b' });
      await chrome.action.setBadgeText({ tabId, text: '!' });
      await chrome.action.setTitle({ tabId, title: `EvoShield: High-risk website address (${host})` });
    } else if (verdict === 'MEDIUM' || verdict === 'REVIEW') {
      await chrome.action.setBadgeBackgroundColor({ tabId, color: '#d99a27' });
      await chrome.action.setBadgeText({ tabId, text: '?' });
      await chrome.action.setTitle({ tabId, title: `EvoShield: Suspicious website address (${host})` });
    } else {
      await chrome.action.setBadgeText({ tabId, text: '' });
      await chrome.action.setTitle({ tabId, title: `EvoShield checked ${host}` });
    }
  } catch (error) {
    await chrome.storage.local.set({
      last_check: {
        enabled: true,
        checked_at: new Date().toISOString(),
        host: new URL(address).hostname,
        risk: 'Check unavailable',
        verdict: 'ERROR',
        message: 'EvoShield could not check this address. Make sure the local EvoShield service is running.'
      }
    });
    await chrome.action.setBadgeBackgroundColor({ tabId, color: '#718096' });
    await chrome.action.setBadgeText({ tabId, text: '…' });
    await chrome.action.setTitle({ tabId, title: `EvoShield check unavailable: ${error.message}` });
  }
}

chrome.tabs.onRemoved.addListener(tabId => lastSent.delete(tabId));
