const API = 'http://127.0.0.1:8000/api/v1/scan/';
const lastSent = new Map();

function safePageAddress(raw) {
  try {
    const url = new URL(raw);
    if (!['http:', 'https:'].includes(url.protocol)) return null;
    // Query strings and fragments often carry session tokens or personal data.
    url.search = '';
    url.hash = '';
    return url.toString();
  } catch {
    return null;
  }
}

chrome.tabs.onUpdated.addListener((tabId, change, tab) => {
  if (change.status !== 'complete' || !tab.url) return;
  const address = safePageAddress(tab.url);
  if (!address || lastSent.get(tabId) === address) return;
  lastSent.set(tabId, address);
  fetch(API, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type: 'url', source: 'browser-extension', content: address, subject: address })
  }).then(response => {
    if (!response.ok) throw new Error(`EvoShield returned ${response.status}`);
  }).catch(error => {
    console.warn('EvoShield could not check this page. Is the local dashboard running?', error);
  });
});

chrome.tabs.onRemoved.addListener(tabId => lastSent.delete(tabId));
