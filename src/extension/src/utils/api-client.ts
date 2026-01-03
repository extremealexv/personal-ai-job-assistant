/**
 * API Client for communicating with the backend
 */

import type { ApiResponse, ResumeData, ApplicationTemplate, ExtensionSettings } from '../types';

class APIClient {
  private baseUrl: string;
  private authToken: string | null = null;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  /**
   * Set authentication token
   */
  setAuthToken(token: string): void {
    this.authToken = token;
  }

  /**
   * Get authentication token
   */
  getAuthToken(): string | null {
    return this.authToken;
  }

  /**
   * Make authenticated API request
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    };

    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const errorText = await response.text();
        return {
          success: false,
          error: `HTTP ${response.status}: ${errorText}`,
        };
      }

      const data = await response.json();
      return {
        success: true,
        data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  /**
   * Authenticate extension with backend
   */
  async authenticate(email: string, password: string): Promise<ApiResponse<{ access_token: string }>> {
    const response = await this.request<{ access_token: string }>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username: email, password }),
    });

    if (response.success && response.data) {
      this.setAuthToken(response.data.access_token);
    }

    return response;
  }

  /**
   * Fetch user's resume data for autofill
   */
  async getResumeData(resumeVersionId?: string): Promise<ApiResponse<ResumeData>> {
    const endpoint = resumeVersionId
      ? `/api/v1/extension/resume-data?version_id=${resumeVersionId}`
      : '/api/v1/extension/resume-data';
    
    return this.request<ResumeData>(endpoint, {
      method: 'GET',
    });
  }

  /**
   * Fetch application template (resume + cover letter for specific job)
   */
  async getApplicationTemplate(jobId: string): Promise<ApiResponse<ApplicationTemplate>> {
    return this.request<ApplicationTemplate>(`/api/v1/extension/application-template/${jobId}`, {
      method: 'GET',
    });
  }

  /**
   * Get user settings
   */
  async getSettings(): Promise<ApiResponse<ExtensionSettings>> {
    return this.request<ExtensionSettings>('/api/v1/extension/settings', {
      method: 'GET',
    });
  }

  /**
   * Update user settings
   */
  async updateSettings(settings: Partial<ExtensionSettings>): Promise<ApiResponse<ExtensionSettings>> {
    return this.request<ExtensionSettings>('/api/v1/extension/settings', {
      method: 'PATCH',
      body: JSON.stringify(settings),
    });
  }

  /**
   * Log autofill activity
   */
  async logActivity(activity: {
    platform: string;
    url: string;
    action: string;
    result: string;
    fieldsCompleted?: number;
    totalFields?: number;
    error?: string;
  }): Promise<ApiResponse<void>> {
    return this.request<void>('/api/v1/extension/activity', {
      method: 'POST',
      body: JSON.stringify(activity),
    });
  }

  /**
   * Download file from backend (resume or cover letter)
   */
  async downloadFile(fileUrl: string): Promise<Blob | null> {
    try {
      const response = await fetch(`${this.baseUrl}${fileUrl}`, {
        headers: {
          'Authorization': `Bearer ${this.authToken}`,
        },
      });

      if (!response.ok) {
        console.error('Failed to download file:', response.statusText);
        return null;
      }

      return await response.blob();
    } catch (error) {
      console.error('Error downloading file:', error);
      return null;
    }
  }
}

// Export singleton instance
export const apiClient = new APIClient();
