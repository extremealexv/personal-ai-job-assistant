/**
 * Lever ATS Strategy
 * 
 * Handles autofill for Lever application forms.
 * Lever is popular among startups and modern companies.
 * 
 * Detection: URL contains "jobs.lever.co" or Lever-specific classes
 * Form Structure: Clean, minimal forms with straightforward field structure
 */

import type { ApplicationData, AutofillResult } from '../../types';
import { BaseATSStrategy } from './base-strategy';
import { logger } from '../../utils/logger';

export class LeverStrategy extends BaseATSStrategy {
  /**
   * Detect if current page is Lever
   */
  detect(): boolean {
    // Check URL
    if (window.location.hostname.includes('jobs.lever.co')) {
      return true;
    }

    // Check for Lever-specific DOM elements
    const leverElements = [
      '.application-form',
      'input[name="name"]',
      'input[name="email"]',
      '.posting-headline',
      '[data-qa="application-form"]',
    ];

    return leverElements.some((selector) => document.querySelector(selector) !== null);
  }

  /**
   * Get platform name
   */
  getPlatformName(): string {
    return 'lever';
  }

  /**
   * Perform autofill for Lever
   */
  async autofill(data: ApplicationData): Promise<AutofillResult> {
    this.data = data;
    this.startTime = Date.now();
    let fieldsFilledCount = 0;

    try {
      logger.info('Starting Lever autofill...');

      // Wait for form to load
      const form = await this.waitForElement('.application-form', 10000);
      if (!form) {
        return this.createErrorResult('Lever form not found');
      }

      // Section 1: Contact Information
      logger.info('Filling contact information...');
      fieldsFilledCount += await this.fillContactInfo();

      // Section 2: Resume Upload
      logger.info('Uploading resume...');
      const resumeUploaded = await this.uploadResume();
      if (resumeUploaded) fieldsFilledCount++;

      // Section 3: Additional Information (if any)
      logger.info('Filling additional information...');
      fieldsFilledCount += await this.fillAdditionalInfo();

      // Section 4: Custom Questions
      logger.info('Filling custom questions...');
      fieldsFilledCount += await this.fillCustomQuestions();

      logger.info(`Lever autofill complete: ${fieldsFilledCount} fields filled`);
      return this.createSuccessResult(fieldsFilledCount);
    } catch (error) {
      logger.error('Lever autofill error:', error);
      return this.createErrorResult('Autofill failed', error);
    }
  }

  /**
   * Fill contact information section
   */
  private async fillContactInfo(): Promise<number> {
    let count = 0;
    const { personalInfo } = this.data!;

    // Full name
    if (this.fillTextField('input[name="name"]', personalInfo.fullName)) {
      count++;
    }

    // Email
    if (this.fillTextField('input[name="email"]', personalInfo.email)) {
      count++;
    }

    // Phone
    if (personalInfo.phone) {
      if (this.fillTextField('input[name="phone"]', personalInfo.phone)) {
        count++;
      }
    }

    // Location/City
    if (personalInfo.location) {
      if (this.fillTextField('input[name="location"]', personalInfo.location)) {
        count++;
      }
    }

    // LinkedIn
    if (personalInfo.linkedinUrl) {
      if (this.fillTextField('input[name="urls[LinkedIn]"]', personalInfo.linkedinUrl)) {
        count++;
      }
      if (this.fillTextField('input[name="linkedin"]', personalInfo.linkedinUrl)) {
        count++;
      }
    }

    // GitHub
    if (personalInfo.githubUrl) {
      if (this.fillTextField('input[name="urls[Github]"]', personalInfo.githubUrl)) {
        count++;
      }
      if (this.fillTextField('input[name="github"]', personalInfo.githubUrl)) {
        count++;
      }
    }

    // Portfolio
    if (personalInfo.portfolioUrl) {
      if (this.fillTextField('input[name="urls[Portfolio]"]', personalInfo.portfolioUrl)) {
        count++;
      }
      if (this.fillTextField('input[name="portfolio"]', personalInfo.portfolioUrl)) {
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
      // Lever typically uses a drag-drop or button upload
      const fileInput = document.querySelector('input[type="file"][name="resume"]') as HTMLInputElement ||
                       document.querySelector('input[type="file"]') as HTMLInputElement;

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
   * Fill additional information
   */
  private async fillAdditionalInfo(): Promise<number> {
    let count = 0;

    try {
      // Lever may have additional text areas for cover letter or comments
      const additionalInfo = document.querySelector('textarea[name="comments"]') as HTMLTextAreaElement;
      
      if (additionalInfo && this.data!.coverLetter) {
        if (this.fillTextField('textarea[name="comments"]', this.data!.coverLetter)) {
          count++;
        }
      }

      // Cover letter field
      const coverLetter = document.querySelector('textarea[name="cover_letter"]') as HTMLTextAreaElement;
      if (coverLetter && this.data!.coverLetter) {
        if (this.fillTextField('textarea[name="cover_letter"]', this.data!.coverLetter)) {
          count++;
        }
      }
    } catch (error) {
      logger.error('Additional info error:', error);
    }

    return count;
  }

  /**
   * Fill custom questions
   * Lever allows custom questions with various field types
   */
  private async fillCustomQuestions(): Promise<number> {
    let count = 0;

    try {
      // Look for custom question sections
      const questionSections = document.querySelectorAll('.application-question');

      for (const section of Array.from(questionSections)) {
        const label = section.querySelector('label')?.textContent?.trim();
        if (!label) continue;

        logger.debug(`Processing custom question: ${label}`);

        // Find input field in this section
        const input = section.querySelector('input, textarea, select') as 
          HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement;

        if (input) {
          const filled = await this.fillCustomField(input, label);
          if (filled) count++;
        }
      }

      // Also check for fields with data-qa attributes
      const customFields = document.querySelectorAll('[data-qa^="application-question"]');
      
      for (const field of Array.from(customFields)) {
        const fieldElement = field as HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement;
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
    // Try parent question section
    const parent = field.closest('.application-question');
    if (parent) {
      const label = parent.querySelector('label');
      if (label) {
        return label.textContent?.trim() || null;
      }
    }

    // Try sibling label
    const prevSibling = field.previousElementSibling;
    if (prevSibling && prevSibling.tagName === 'LABEL') {
      return prevSibling.textContent?.trim() || null;
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
    if (labelLower.includes('authorized') && labelLower.includes('work')) {
      if (field.tagName === 'SELECT') {
        return this.fillSelectField(`#${field.id}`, 'Yes') || 
               this.fillSelectField(`[name="${field.name}"]`, 'Yes');
      } else if (field.type === 'radio') {
        return this.fillRadioButton(field.name, 'yes');
      } else if (field.type === 'checkbox') {
        return this.fillCheckbox(`#${field.id}`, true);
      } else {
        return this.fillTextField(`#${field.id}`, 'Yes');
      }
    }

    // Sponsorship
    if (labelLower.includes('sponsorship') || labelLower.includes('visa')) {
      if (field.tagName === 'SELECT') {
        return this.fillSelectField(`#${field.id}`, 'No') ||
               this.fillSelectField(`[name="${field.name}"]`, 'No');
      } else if (field.type === 'radio') {
        return this.fillRadioButton(field.name, 'no');
      } else {
        return this.fillTextField(`#${field.id}`, 'No');
      }
    }

    // Years of experience
    if (labelLower.includes('years') && labelLower.includes('experience')) {
      if (workExperience && workExperience.length > 0) {
        const totalYears = this.calculateTotalExperience(workExperience);
        return this.fillTextField(`#${field.id}`, String(totalYears)) ||
               this.fillTextField(`[name="${field.name}"]`, String(totalYears));
      }
    }

    // LinkedIn
    if (labelLower.includes('linkedin')) {
      if (personalInfo.linkedinUrl) {
        return this.fillTextField(`#${field.id}`, personalInfo.linkedinUrl) ||
               this.fillTextField(`[name="${field.name}"]`, personalInfo.linkedinUrl);
      }
    }

    // Portfolio/Website
    if (labelLower.includes('portfolio') || labelLower.includes('website')) {
      if (personalInfo.portfolioUrl) {
        return this.fillTextField(`#${field.id}`, personalInfo.portfolioUrl) ||
               this.fillTextField(`[name="${field.name}"]`, personalInfo.portfolioUrl);
      }
    }

    // Gender/Diversity questions (skip for privacy)
    if (labelLower.includes('gender') || 
        labelLower.includes('race') || 
        labelLower.includes('ethnicity') ||
        labelLower.includes('veteran')) {
      logger.info(`Skipping demographic question: ${label}`);
      return false;
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
