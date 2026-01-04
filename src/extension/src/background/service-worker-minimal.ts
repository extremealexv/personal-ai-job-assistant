/**
 * Minimal Service Worker - Testing
 */

console.log('=== MINIMAL SERVICE WORKER STARTED ===');

chrome.runtime.onInstalled.addListener(() => {
  console.log('=== EXTENSION INSTALLED ===');
});

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  console.log('=== MESSAGE RECEIVED ===', message);
  sendResponse({ success: true, message: 'Service worker is alive!' });
  return true;
});

console.log('=== SERVICE WORKER READY ===');
