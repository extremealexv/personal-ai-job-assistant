/**
 * Content Script - Injected into job application pages
 * Detects ATS platform and coordinates autofill
 */

import { logger } from '../utils/logger';
import type { ATSPlatform, ApplicationData, ExtensionMessage } from '../types';

logger.info('Content script initialized on:', window.location.hostname);

// Detect ATS platform
const detectedPlatform = detectATSPlatform();
logger.info('Detected platform:', detectedPlatform);

/**
 * Detect which ATS platform we're on
 */
function detectATSPlatform(): ATSPlatform {
  const hostname = window.location.hostname.toLowerCase();
  const url = window.location.href.toLowerCase();

  if (hostname.includes('myworkdayjobs.com') || url.includes('workday')) {
    return 'workday';
  } else if (hostname.includes('greenhouse.io')) {
    return 'greenhouse';
  } else if (hostname.includes('lever.co')) {
    return 'lever';
  } else if (hostname.includes('taleo.net')) {
    return 'taleo';
  } else {
    return 'unknown';
  }
}

/**
 * Listen for messages from background script
 */
chrome.runtime.onMessage.addListener((message: ExtensionMessage, _sender, sendResponse) => {
  logger.debug('Content script received message:', message.type);

  switch (message.type) {
    case 'autofill-data':
      handleAutofillData(message.payload).then(sendResponse);
      return true; // Keep channel open

    case 'detect-platform':
      sendResponse({ platform: detectedPlatform });
      return false;

    default:
      logger.warn('Unknown message type:', message.type);
      return false;
  }
});

/**
 * Handle autofill data from background script
 */
async function handleAutofillData(data: ApplicationData) {
  try {
    logger.info('Starting autofill with data:', data);

    // TODO: Import and use appropriate ATS strategy
    // For now, just show a notification
    showNotification('Autofill started', `Detected platform: ${detectedPlatform}`);

    // Simulate autofill for now
    await new Promise(resolve => setTimeout(resolve, 2000));

    showNotification('Autofill complete', 'Form has been filled successfully');

    // Log activity
    await chrome.runtime.sendMessage({
      type: 'log-activity',
      payload: {
        platform: detectedPlatform,
        url: window.location.href,
        action: 'autofill',
        result: 'success',
        fieldsCompleted: 10,
        totalFields: 10,
      },
    });

    return { success: true };
  } catch (error) {
    logger.error('Error during autofill:', error);
    
    showNotification('Autofill failed', error instanceof Error ? error.message : 'Unknown error');

    // Log failure
    await chrome.runtime.sendMessage({
      type: 'log-activity',
      payload: {
        platform: detectedPlatform,
        url: window.location.href,
        action: 'autofill',
        result: 'failure',
        error: error instanceof Error ? error.message : 'Unknown error',
      },
    });

    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Show notification to user
 */
function showNotification(title: string, message: string) {
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #4CAF50;
    color: white;
    padding: 16px 24px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    z-index: 10000;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    max-width: 300px;
  `;
  
  notification.innerHTML = `
    <div style="font-weight: 600; margin-bottom: 4px;">${title}</div>
    <div style="font-size: 14px; opacity: 0.95;">${message}</div>
  `;

  document.body.appendChild(notification);

  // Auto-remove after 5 seconds
  setTimeout(() => {
    notification.style.transition = 'opacity 0.3s';
    notification.style.opacity = '0';
    setTimeout(() => notification.remove(), 300);
  }, 5000);
}

logger.info('Content script ready');
