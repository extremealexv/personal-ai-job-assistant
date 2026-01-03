/**
 * Greenhouse ATS Strategy
 * 
 * Handles autofill for Greenhouse application forms.
 * Greenhouse is popular among tech companies and startups.
 * 
 * Detection: URL contains "boards.greenhouse.io" or Greenhouse-specific classes
 * Form Structure: Single-page or multi-step forms with semantic field IDs
 */

import type { ApplicationData, AutofillResult } from '../../types';
import { BaseATSStrategy } from './base-strategy';
import { logger } from '../../utils/logger';

export class GreenhouseStrategy extends BaseATSStrategy {
  /**
   * Detect if current page is Greenhouse
   */
  detect(): boolean {
    // Check URL
    if (window.location.hostname.includes('boards.greenhouse.io')) {
      return true;
    }

    // Check for Greenhouse-specific DOM elements
    const greenhouseElements = [
      '#first_name',
      '#last_name',
      '#email',
      '.application-form',
      '[data-source="greenhouse"]',
    ];

    return greenhouseElements.some((selector) => document.querySelector(selector) !== null);
  }

  /**
   * Get platform name
   */
  getPlatformName(): string {
    return 'greenhouse';
  }

  /**
   * Perform autofill for Greenhouse
   */
  async autofill(data: ApplicationData): Promise<AutofillResult> {
    this.data = data;
    this.startTime = Date.now();
    let fieldsFilledCount = 0;

    try {
      logger.info('Starting Greenhouse autofill...');

      // Wait for form to load
      const form = await this.waitForElement('.application-form', 10000);
      if (!form) {
        return this.createErrorResult('Greenhouse form not found');
      }

      // Section 1: Basic Information
      logger.info('Filling basic information...');
      fieldsFilledCount += await this.fillBasicInfo();

      // Section 2: Additional Information
      logger.info('Filling additional information...');
      fieldsFilledCount += await this.fillAdditionalInfo();

      // Section 3: Resume Upload
      logger.info('Uploading resume...');
      const resumeUploaded = await this.uploadResume();
      if (resumeUploaded) fieldsFilledCount++;

      // Section 4: Cover Letter
      if (data.coverLetter) {
        logger.info('Filling cover letter...');
        const coverLetterFilled = await this.fillCoverLetter();
        if (coverLetterFilled) fieldsFilledCount++;
      }

      // Section 5: Custom Questions (if any)
      logger.info('Filling custom questions...');
      fieldsFilledCount += await this.fillCustomQuestions();

      logger.info(`Greenhouse autofill complete: ${fieldsFilledCount} fields filled`);
      return this.createSuccessResult(fieldsFilledCount);
    } catch (error) {
      logger.error('Greenhouse autofill error:', error);
      return this.createErrorResult('Autofill failed', error);
    }
  }

  /**
   * Fill basic information section
   */
  private async fillBasicInfo(): Promise<number> {
    let count = 0;
    const { personalInfo } = this.data!;

    // First name
    if (this.fillTextField('#first_name', personalInfo.firstName || personalInfo.fullName.split(' ')[0])) {
      count++;
    }

    // Last name
    const lastName = personalInfo.lastName || personalInfo.fullName.split(' ').slice(1).join(' ');
    if (this.fillTextField('#last_name', lastName)) {
      count++;
    }

    // Email
    if (this.fillTextField('#email', personalInfo.email)) {
      count++;
    }

    // Phone
    if (personalInfo.phone) {
      if (this.fillTextField('#phone', personalInfo.phone)) {
        count++;
      }
    }

    // Location
    if (personalInfo.location) {
      // Greenhouse may have separate city/state/country fields or combined
      if (this.fillTextField('#location', personalInfo.location)) {
        count++;
      }
      if (this.fillTextField('#city', personalInfo.location)) {
        count++;
      }
    }

    return count;
  }

  /**
   * Fill additional information
   */
  private async fillAdditionalInfo(): Promise<number> {
    let count = 0;
    const { personalInfo } = this.data!;

    // LinkedIn
    if (personalInfo.linkedinUrl) {
      if (this.fillTextField('#linkedin_url', personalInfo.linkedinUrl)) {
        count++;
      }
      if (this.fillTextField('input[name="linkedin"]', personalInfo.linkedinUrl)) {
        count++;
      }
    }

    // GitHub
    if (personalInfo.githubUrl) {
      if (this.fillTextField('#github_url', personalInfo.githubUrl)) {
        count++;
      }
      if (this.fillTextField('input[name="github"]', personalInfo.githubUrl)) {
        count++;
      }
    }

    // Website/Portfolio
    if (personalInfo.portfolioUrl) {
      if (this.fillTextField('#website', personalInfo.portfolioUrl)) {
        count++;
      }
      if (this.fillTextField('input[name="website"]', personalInfo.portfolioUrl)) {
        count++;
      }
    }

    return count;
  }

  /**
   * Upload resume file
   */
  private async uploadResume(): Promise<boolean> {
    try {
      // Greenhouse typically uses a specific resume input
      const fileInput = document.querySelector('#resume') as HTMLInputElement ||
                       document.querySelector('input[type="file"][name="resume"]') as HTMLInputElement;

      if (!fileInput) {
        logger.warn('Resume file input not found');
        return false;
      }

      logger.info('Resume upload field found (file would be uploaded here)');
      
      // TODO: Implement actual file upload once backend integration is complete
      return false;
    } catch (error) {
      logger.error('Resume upload error:', error);
      return false;
    }
  }

  /**
   * Fill cover letter
   */
  private async fillCoverLetter(): Promise<boolean> {
    try {
      // Greenhouse may have a cover letter text area
      const textArea = document.querySelector('#cover_letter') as HTMLTextAreaElement ||
                      document.querySelector('textarea[name="cover_letter"]') as HTMLTextAreaElement;

      if (textArea && this.data!.coverLetter) {
        return this.fillTextField('#cover_letter', this.data!.coverLetter) ||
               this.fillTextField('textarea[name="cover_letter"]', this.data!.coverLetter);
      }

      // Or a file upload
      const fileInput = document.querySelector('input[type="file"][name="cover_letter"]') as HTMLInputElement;
      if (fileInput) {
        logger.info('Cover letter file upload found');
        // TODO: Implement file upload
        return false;
      }

      return false;
    } catch (error) {
      logger.error('Cover letter error:', error);
      return false;
    }
  }

  /**
   * Fill custom questions
   * Greenhouse allows employers to add custom questions
   */
  private async fillCustomQuestions(): Promise<number> {
    let count = 0;

    try {
      // Look for custom question fields
      const customFields = document.querySelectorAll('[id^="job_application_answers_"]');

      for (const field of Array.from(customFields)) {
        const fieldElement = field as HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement;
        const fieldId = fieldElement.id;
        const fieldType = fieldElement.type || fieldElement.tagName.toLowerCase();

        logger.debug(`Found custom field: ${fieldId} (${fieldType})`);

        // Try to intelligently fill based on field label
        const label = this.getFieldLabel(fieldElement);
        if (label) {
          const filled = await this.fillCustomField(fieldElement, label);
          if (filled) count++;
        }
      }
    } catch (error) {
      logger.error('Custom questions error:', error);
    }

    return count;
  }

  /**
   * Get label text for a field
   */
  private getFieldLabel(field: HTMLElement): string | null {
    // Try to find associated label
    const fieldId = field.id;
    if (fieldId) {
      const label = document.querySelector(`label[for="${fieldId}"]`);
      if (label) {
        return label.textContent?.trim() || null;
      }
    }

    // Try parent element
    const parent = field.closest('.field, .form-group, .question');
    if (parent) {
      const label = parent.querySelector('label');
      if (label) {
        return label.textContent?.trim() || null;
      }
    }

    return null;
  }

  /**
   * Fill a custom field based on its label
   */
  private async fillCustomField(
    field: HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement,
    label: string
  ): Promise<boolean> {
    const labelLower = label.toLowerCase();
    const { personalInfo, workExperience } = this.data!;

    // Authorization to work
    if (labelLower.includes('authorized to work') || labelLower.includes('work authorization')) {
      if (field.tagName === 'SELECT') {
        return this.fillSelectField(`#${field.id}`, 'Yes');
      } else if (field.type === 'radio') {
        return this.fillRadioButton(field.name, 'yes');
      }
    }

    // Sponsorship
    if (labelLower.includes('sponsorship') || labelLower.includes('visa')) {
      if (field.tagName === 'SELECT') {
        return this.fillSelectField(`#${field.id}`, 'No');
      } else if (field.type === 'radio') {
        return this.fillRadioButton(field.name, 'no');
      }
    }

    // Years of experience
    if (labelLower.includes('years of experience') || labelLower.includes('years experience')) {
      if (workExperience && workExperience.length > 0) {
        const totalYears = this.calculateTotalExperience(workExperience);
        return this.fillTextField(`#${field.id}`, String(totalYears));
      }
    }

    // LinkedIn
    if (labelLower.includes('linkedin')) {
      if (personalInfo.linkedinUrl) {
        return this.fillTextField(`#${field.id}`, personalInfo.linkedinUrl);
      }
    }

    // Portfolio/Website
    if (labelLower.includes('portfolio') || labelLower.includes('website')) {
      if (personalInfo.portfolioUrl) {
        return this.fillTextField(`#${field.id}`, personalInfo.portfolioUrl);
      }
    }

    return false;
  }

  /**
   * Calculate total years of experience
   */
  private calculateTotalExperience(workExperience: any[]): number {
    let totalMonths = 0;

    for (const exp of workExperience) {
      const startDate = new Date(exp.startDate);
      const endDate = exp.isCurrent ? new Date() : new Date(exp.endDate);
      
      const months = (endDate.getFullYear() - startDate.getFullYear()) * 12 +
                     (endDate.getMonth() - startDate.getMonth());
      
      totalMonths += months;
    }

    return Math.floor(totalMonths / 12);
  }
}
