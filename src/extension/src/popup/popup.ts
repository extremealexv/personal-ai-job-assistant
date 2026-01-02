/**
 * Popup Script - UI logic for extension popup
 */

import { storage } from '../utils/storage';
import { apiClient } from '../utils/api-client';
import { logger } from '../utils/logger';
import type { ExtensionSettings } from '../types';

// DOM Elements
const authSection = document.getElementById('authSection') as HTMLElement;
const mainSection = document.getElementById('mainSection') as HTMLElement;
const loginForm = document.getElementById('loginForm') as HTMLFormElement;
const authError = document.getElementById('authError') as HTMLElement;
const statusIndicator = document.getElementById('statusIndicator') as HTMLElement;
const statusText = document.getElementById('statusText') as HTMLElement;
const platformName = document.getElementById('platformName') as HTMLElement;
const autofillBtn = document.getElementById('autofillBtn') as HTMLButtonElement;
const saveSettingsBtn = document.getElementById('saveSettings') as HTMLButtonElement;
const logoutBtn = document.getElementById('logoutBtn') as HTMLButtonElement;
const activityList = document.getElementById('activityList') as HTMLElement;

// Settings checkboxes
const autoSubmitCheck = document.getElementById('autoSubmit') as HTMLInputElement;
const enableWorkdayCheck = document.getElementById('enableWorkday') as HTMLInputElement;
const enableGreenhouseCheck = document.getElementById('enableGreenhouse') as HTMLInputElement;
const enableLeverCheck = document.getElementById('enableLever') as HTMLInputElement;
const enableTaleoCheck = document.getElementById('enableTaleo') as HTMLInputElement;

// Initialize popup
async function init() {
  logger.info('Popup initialized');

  // Check authentication status
  const authToken = await storage.getAuthToken();
  const settings = await storage.getSettings();

  if (authToken) {
    apiClient.setAuthToken(authToken);
    showMainSection();
    await loadSettings();
    await loadActivityLog();
    await detectPlatform();
  } else {
    showAuthSection();
  }

  setupEventListeners();
}

/**
 * Show authentication section
 */
function showAuthSection() {
  authSection.style.display = 'block';
  mainSection.style.display = 'none';
  statusIndicator.classList.remove('connected');
  statusText.textContent = 'Not authenticated';
}

/**
 * Show main section (after authentication)
 */
function showMainSection() {
  authSection.style.display = 'none';
  mainSection.style.display = 'block';
  statusIndicator.classList.add('connected');
  statusText.textContent = 'Connected';
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
  // Login form
  loginForm.addEventListener('submit', handleLogin);

  // Autofill button
  autofillBtn.addEventListener('click', handleAutofill);

  // Save settings
  saveSettingsBtn.addEventListener('click', handleSaveSettings);

  // Logout
  logoutBtn.addEventListener('click', handleLogout);

  // Tabs
  const tabButtons = document.querySelectorAll('.tab-btn');
  tabButtons.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const target = e.target as HTMLButtonElement;
      const tabName = target.dataset.tab;
      switchTab(tabName!);
    });
  });
}

/**
 * Handle login
 */
async function handleLogin(e: Event) {
  e.preventDefault();

  const email = (document.getElementById('email') as HTMLInputElement).value;
  const password = (document.getElementById('password') as HTMLInputElement).value;

  try {
    authError.style.display = 'none';
    const response = await apiClient.authenticate(email, password);

    if (response.success && response.data) {
      await storage.setAuthToken(response.data.access_token);
      showMainSection();
      await loadSettings();
      await detectPlatform();
      logger.info('Login successful');
    } else {
      showError(response.error || 'Login failed');
    }
  } catch (error) {
    showError(error instanceof Error ? error.message : 'Login failed');
  }
}

/**
 * Handle autofill button click
 */
async function handleAutofill() {
  try {
    autofillBtn.disabled = true;
    autofillBtn.textContent = 'Filling...';

    // Get current tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab.id) {
      throw new Error('No active tab found');
    }

    // Send message to background script to start autofill
    const response = await chrome.runtime.sendMessage({
      type: 'autofill-start',
    });

    if (response.success) {
      logger.info('Autofill started successfully');
      setTimeout(() => {
        autofillBtn.textContent = '✨ Fill Application';
        autofillBtn.disabled = false;
      }, 2000);
    } else {
      throw new Error(response.error || 'Autofill failed');
    }
  } catch (error) {
    logger.error('Autofill error:', error);
    autofillBtn.textContent = '✨ Fill Application';
    autofillBtn.disabled = false;
    alert(error instanceof Error ? error.message : 'Autofill failed');
  }
}

/**
 * Load settings from storage
 */
async function loadSettings() {
  const settings = await storage.getSettings();
  
  autoSubmitCheck.checked = settings.autoSubmit;
  enableWorkdayCheck.checked = settings.enabledPlatforms.workday;
  enableGreenhouseCheck.checked = settings.enabledPlatforms.greenhouse;
  enableLeverCheck.checked = settings.enabledPlatforms.lever;
  enableTaleoCheck.checked = settings.enabledPlatforms.taleo;
}

/**
 * Handle save settings
 */
async function handleSaveSettings() {
  const updates: Partial<ExtensionSettings> = {
    autoSubmit: autoSubmitCheck.checked,
    enabledPlatforms: {
      workday: enableWorkdayCheck.checked,
      greenhouse: enableGreenhouseCheck.checked,
      lever: enableLeverCheck.checked,
      taleo: enableTaleoCheck.checked,
    },
  };

  await storage.updateSettings(updates);
  
  // Show success feedback
  saveSettingsBtn.textContent = 'Saved!';
  setTimeout(() => {
    saveSettingsBtn.textContent = 'Save Settings';
  }, 2000);

  logger.info('Settings saved');
}

/**
 * Handle logout
 */
async function handleLogout() {
  await storage.clearAuthToken();
  apiClient.setAuthToken('');
  showAuthSection();
  loginForm.reset();
  logger.info('Logged out');
}

/**
 * Detect platform on current tab
 */
async function detectPlatform() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab.id) {
      return;
    }

    const response = await chrome.tabs.sendMessage(tab.id, {
      type: 'detect-platform',
    });

    if (response && response.platform) {
      platformName.textContent = response.platform.charAt(0).toUpperCase() + response.platform.slice(1);
    }
  } catch (error) {
    platformName.textContent = 'Not on a job application page';
    logger.debug('Platform detection failed:', error);
  }
}

/**
 * Load activity log
 */
async function loadActivityLog() {
  const log = await storage.getActivityLog();
  
  if (log.length === 0) {
    activityList.innerHTML = '<p class="empty-state">No activity yet</p>';
    return;
  }

  activityList.innerHTML = log
    .reverse()
    .slice(0, 10)
    .map((entry) => {
      const date = new Date(entry.timestamp);
      const statusClass = entry.result === 'success' ? 'success' : 'failure';
      
      return `
        <div class="activity-item ${statusClass}">
          <div>
            <span class="activity-platform">${entry.platform}</span>
            - ${entry.action}
            ${entry.fieldsCompleted ? `(${entry.fieldsCompleted}/${entry.totalFields} fields)` : ''}
          </div>
          <div class="activity-time">${date.toLocaleString()}</div>
        </div>
      `;
    })
    .join('');
}

/**
 * Switch tabs
 */
function switchTab(tabName: string) {
  // Update buttons
  document.querySelectorAll('.tab-btn').forEach((btn) => {
    btn.classList.remove('active');
  });
  document.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');

  // Update panes
  document.querySelectorAll('.tab-pane').forEach((pane) => {
    pane.classList.remove('active');
  });
  document.getElementById(`${tabName}Tab`)?.classList.add('active');

  // Reload activity log if switching to activity tab
  if (tabName === 'activity') {
    loadActivityLog();
  }
}

/**
 * Show error message
 */
function showError(message: string) {
  authError.textContent = message;
  authError.style.display = 'block';
}

// Initialize on load
init();
