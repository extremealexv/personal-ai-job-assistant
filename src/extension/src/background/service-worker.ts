/**
 * Background Service Worker (Manifest V3)
 * Handles extension lifecycle, message passing, and API coordination
 */

console.log('=== SERVICE WORKER STARTING ===');

import { storage } from '../utils/storage';
import { apiClient } from '../utils/api-client';
import { logger } from '../utils/logger';
import type { ExtensionMessage } from '../types';

console.log('=== IMPORTS SUCCESSFUL ===');

try {
  logger.info('Background service worker initialized');
  console.log('=== LOGGER WORKS ===');
} catch (error) {
  console.error('Logger init failed:', error);
}

// Initialize extension on install
chrome.runtime.onInstalled.addListener(async (details) => {
  try {
    console.log('=== ON INSTALLED TRIGGERED ===', details.reason);
    
    if (details.reason === 'install') {
      logger.info('Extension installed');
      
      // Set default settings
      await storage.updateSettings({
        apiBaseUrl: 'http://localhost:8000',
        enabledPlatforms: {
          workday: true,
          greenhouse: true,
          lever: true,
          taleo: true,
        },
        autoSubmit: false,
      });
      
      // Open welcome page
      chrome.tabs.create({ url: 'popup.html' });
    } else if (details.reason === 'update') {
      logger.info('Extension updated');
    }
    
    console.log('=== ON INSTALLED COMPLETE ===');
  } catch (error) {
    console.error('=== ON INSTALLED ERROR ===', error);
  }
});

// Handle messages from content scripts and popup
chrome.runtime.onMessage.addListener((message: ExtensionMessage, sender, sendResponse) => {
  try {
    console.log('=== BACKGROUND RECEIVED MESSAGE ===', message.type, message);
    logger.debug('Received message:', message.type);

    switch (message.type) {
      case 'get-settings':
        handleGetSettings().then(sendResponse).catch((err) => {
          console.error('get-settings error:', err);
          sendResponse({ success: false, error: String(err) });
        });
        return true; // Keep channel open for async response

      case 'update-settings':
        handleUpdateSettings(message.payload).then(sendResponse).catch((err) => {
          console.error('update-settings error:', err);
          sendResponse({ success: false, error: String(err) });
        });
        return true;

      case 'autofill-start':
        console.log('=== HANDLING AUTOFILL START ===', message.payload);
        handleAutofillStart(message.payload?.tabId || sender.tab?.id).then(sendResponse).catch((err) => {
          console.error('autofill-start error:', err);
          sendResponse({ success: false, error: String(err) });
        });
        return true;

      case 'log-activity':
        handleLogActivity(message.payload).then(sendResponse).catch((err) => {
          console.error('log-activity error:', err);
          sendResponse({ success: false, error: String(err) });
        });
        return true;

      default:
        logger.warn('Unknown message type:', message.type);
        sendResponse({ success: false, error: 'Unknown message type' });
        return false;
    }
  } catch (error) {
    console.error('=== MESSAGE HANDLER ERROR ===', error);
    sendResponse({ success: false, error: String(error) });
    return false;
  }
});

/**
 * Get extension settings
 */
async function handleGetSettings() {
  try {
    const settings = await storage.getSettings();
    const authToken = await storage.getAuthToken();
    
    return {
      success: true,
      data: {
        ...settings,
        isAuthenticated: !!authToken,
      },
    };
  } catch (error) {
    logger.error('Error getting settings:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Update extension settings
 */
async function handleUpdateSettings(updates: any) {
  try {
    await storage.updateSettings(updates);
    logger.info('Settings updated:', updates);
    
    return { success: true };
  } catch (error) {
    logger.error('Error updating settings:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Handle autofill start request
 */
async function handleAutofillStart(tabId?: number) {
  try {
    logger.info('handleAutofillStart called with tabId:', tabId);

    if (!tabId) {
      throw new Error('No tab ID provided');
    }

    // Get auth token
    const authToken = await storage.getAuthToken();
    logger.info('Auth token retrieved:', authToken ? 'yes' : 'no');
    
    if (!authToken) {
      return {
        success: false,
        error: 'Not authenticated. Please log in first.',
      };
    }

    // Set API client token
    apiClient.setAuthToken(authToken);

    // Get resume data
    logger.info('Fetching resume data...');
    const settings = await storage.getSettings();
    const resumeResponse = await apiClient.getResumeData(settings.defaultResumeVersionId);
    
    logger.info('Resume response:', resumeResponse.success);
    
    if (!resumeResponse.success || !resumeResponse.data) {
      return {
        success: false,
        error: resumeResponse.error || 'Failed to fetch resume data',
      };
    }

    // Transform ResumeData to ApplicationData format
    const applicationData = {
      personalInfo: resumeResponse.data.personalInfo,
      workExperience: resumeResponse.data.workExperiences || [],
      workExperiences: resumeResponse.data.workExperiences || [],
      education: resumeResponse.data.education || [],
      skills: resumeResponse.data.skills || [],
    };

    logger.info('Sending autofill-data message to tab:', tabId);

    // Send application data to content script
    const messageResponse = await chrome.tabs.sendMessage(tabId, {
      type: 'autofill-data',
      payload: applicationData,
    });

    logger.info('Content script response:', messageResponse);
    logger.info('Sent application data to content script');
    
    return { success: true };
  } catch (error) {
    logger.error('Error handling autofill start:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Log activity to backend and local storage
 */
async function handleLogActivity(activity: any) {
  try {
    // Store locally
    await storage.addActivityLogEntry({
      timestamp: Date.now(),
      ...activity,
    });

    // Send to backend (optional, non-blocking)
    const authToken = await storage.getAuthToken();
    if (authToken) {
      apiClient.setAuthToken(authToken);
      await apiClient.logActivity(activity).catch((error) => {
        logger.warn('Failed to log activity to backend:', error);
      });
    }

    return { success: true };
  } catch (error) {
    logger.error('Error logging activity:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

// Keep service worker alive (workaround for Chrome's 5-minute timeout)
chrome.alarms.create('keep-alive', { periodInMinutes: 1 });
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'keep-alive') {
    logger.debug('Service worker keep-alive ping');
  }
});

logger.info('Background service worker ready');
