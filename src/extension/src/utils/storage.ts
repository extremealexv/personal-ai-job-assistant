/**
 * Storage utility for Chrome extension storage API
 */

import { StorageKeys } from '../types';
import type { ExtensionSettings, ActivityLogEntry } from '../types';

class StorageManager {
  /**
   * Get item from storage
   */
  async get<T>(key: string): Promise<T | null> {
    try {
      const result = await chrome.storage.local.get(key);
      return result[key] || null;
    } catch (error) {
      console.error('Storage get error:', error);
      return null;
    }
  }

  /**
   * Set item in storage
   */
  async set(key: string, value: any): Promise<boolean> {
    try {
      await chrome.storage.local.set({ [key]: value });
      return true;
    } catch (error) {
      console.error('Storage set error:', error);
      return false;
    }
  }

  /**
   * Remove item from storage
   */
  async remove(key: string): Promise<boolean> {
    try {
      await chrome.storage.local.remove(key);
      return true;
    } catch (error) {
      console.error('Storage remove error:', error);
      return false;
    }
  }

  /**
   * Clear all storage
   */
  async clear(): Promise<boolean> {
    try {
      await chrome.storage.local.clear();
      return true;
    } catch (error) {
      console.error('Storage clear error:', error);
      return false;
    }
  }

  /**
   * Get extension settings
   */
  async getSettings(): Promise<ExtensionSettings> {
    const settings = await this.get<ExtensionSettings>(StorageKeys.SETTINGS);
    
    // Return default settings if none exist
    if (!settings) {
      return {
        apiBaseUrl: 'http://localhost:8000',
        enabledPlatforms: {
          workday: true,
          greenhouse: true,
          lever: true,
          taleo: true,
        },
        autoSubmit: false,
      };
    }

    return settings;
  }

  /**
   * Update extension settings
   */
  async updateSettings(updates: Partial<ExtensionSettings>): Promise<boolean> {
    const currentSettings = await this.getSettings();
    const newSettings = { ...currentSettings, ...updates };
    return this.set(StorageKeys.SETTINGS, newSettings);
  }

  /**
   * Get auth token
   */
  async getAuthToken(): Promise<string | null> {
    return this.get<string>(StorageKeys.AUTH_TOKEN);
  }

  /**
   * Set auth token
   */
  async setAuthToken(token: string): Promise<boolean> {
    return this.set(StorageKeys.AUTH_TOKEN, token);
  }

  /**
   * Clear auth token (logout)
   */
  async clearAuthToken(): Promise<boolean> {
    return this.remove(StorageKeys.AUTH_TOKEN);
  }

  /**
   * Get activity log
   */
  async getActivityLog(): Promise<ActivityLogEntry[]> {
    const log = await this.get<ActivityLogEntry[]>(StorageKeys.ACTIVITY_LOG);
    return log || [];
  }

  /**
   * Add activity log entry
   */
  async addActivityLogEntry(entry: ActivityLogEntry): Promise<boolean> {
    const log = await this.getActivityLog();
    log.push(entry);
    
    // Keep only last 100 entries
    const trimmedLog = log.slice(-100);
    
    return this.set(StorageKeys.ACTIVITY_LOG, trimmedLog);
  }

  /**
   * Clear activity log
   */
  async clearActivityLog(): Promise<boolean> {
    return this.remove(StorageKeys.ACTIVITY_LOG);
  }

  /**
   * Get last sync timestamp
   */
  async getLastSync(): Promise<number | null> {
    return this.get<number>(StorageKeys.LAST_SYNC);
  }

  /**
   * Update last sync timestamp
   */
  async updateLastSync(): Promise<boolean> {
    return this.set(StorageKeys.LAST_SYNC, Date.now());
  }
}

// Export singleton instance
export const storage = new StorageManager();
