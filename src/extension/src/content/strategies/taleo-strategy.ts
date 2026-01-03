/**
 * Taleo ATS Strategy
 * 
 * Handles autofill for Taleo application forms.
 * Taleo is an older but still widely used ATS, especially in large enterprises.
 * 
 * Detection: URL contains "taleo.net" or Taleo-specific classes
 * Form Structure: Multi-step forms with complex navigation
 */

import type { ApplicationData, AutofillResult } from '../../types';
import { BaseATSStrategy } from './base-strategy';
import { logger } from '../../utils/logger';

export class TaleoStrategy extends BaseATSStrategy {
  /**
   * Detect if current page is Taleo
   */
  detect(): boolean {
    // Check URL
    if (window.location.hostname.includes('taleo.net')) {
      return true;
    }

    // Check for Taleo-specific DOM elements
    const taleoElements = [
      '#requisitionDescriptionInterface',
      '.taleoContent',
      '.requisitionDescriptionInterface',
      'form[name="taleoForm"]',
      '[id*="taleo"]',
    ];

    return taleoElements.some((selector) => document.querySelector(selector) !== null);
  }

  /**
   * Get platform name
   */
  getPlatformName(): string {
    return 'taleo';
  }

  /**
   * Perform autofill for Taleo
   */
  async autofill(data: ApplicationData): Promise<AutofillResult> {
    this.data = data;
    this.startTime = Date.now();
    let fieldsFilledCount = 0;

    try {
      logger.info('Starting Taleo autofill...');

      // Taleo forms are often multi-step, so we need to detect current step
      const currentStep = await this.detectCurrentStep();
      logger.info(`Detected Taleo step: ${currentStep}`);

      switch (currentStep) {
        case 'profile':
          fieldsFilledCount += await this.fillProfileStep();
          break;

        case 'experience':
          fieldsFilledCount += await this.fillExperienceStep();
          break;

        case 'education':
          fieldsFilledCount += await this.fillEducationStep();
          break;

        case 'questionnaire':
          fieldsFilledCount += await this.fillQuestionnaireStep();
          break;

        case 'attachments':
          const uploaded = await this.fillAttachmentsStep();
          if (uploaded) fieldsFilledCount++;
          break;

        default:
          logger.warn(`Unknown Taleo step: ${currentStep}`);
          // Try to fill whatever fields are visible
          fieldsFilledCount += await this.fillVisibleFields();
      }

      logger.info(`Taleo autofill complete: ${fieldsFilledCount} fields filled`);
      return this.createSuccessResult(fieldsFilledCount);
    } catch (error) {
      logger.error('Taleo autofill error:', error);
      return this.createErrorResult('Autofill failed', error);
    }
  }

  /**
   * Detect current step in Taleo's multi-step form
   */
  private async detectCurrentStep(): Promise<string> {
    // Check page title or heading
    const heading = document.querySelector('h1, .pageTitle')?.textContent?.toLowerCase() || '';
    
    if (heading.includes('profile') || heading.includes('personal information')) {
      return 'profile';
    }
    if (heading.includes('experience') || heading.includes('work history')) {
      return 'experience';
    }
    if (heading.includes('education')) {
      return 'education';
    }
    if (heading.includes('question') || heading.includes('assessment')) {
      return 'questionnaire';
    }
    if (heading.includes('attachment') || heading.includes('resume')) {
      return 'attachments';
    }

    // Check for specific field patterns
    if (document.querySelector('input[name*="firstName"], input[name*="lastName"]')) {
      return 'profile';
    }
    if (document.querySelector('input[name*="employer"], input[name*="jobTitle"]')) {
      return 'experience';
    }
    if (document.querySelector('input[name*="school"], input[name*="degree"]')) {
      return 'education';
    }
    if (document.querySelector('input[type="file"]')) {
      return 'attachments';
    }

    return 'unknown';
  }

  /**
   * Fill profile/personal information step
   */
  private async fillProfileStep(): Promise<number> {
    let count = 0;
    const { personalInfo } = this.data!;

    // First name
    const firstNameFields = [
      'input[name*="firstName"]',
      'input[id*="firstName"]',
      'input[name="first_name"]',
    ];
    for (const selector of firstNameFields) {
      if (this.fillTextField(selector, personalInfo.firstName || personalInfo.fullName.split(' ')[0])) {
        count++;
        break;
      }
    }

    // Last name
    const lastNameFields = [
      'input[name*="lastName"]',
      'input[id*="lastName"]',
      'input[name="last_name"]',
    ];
    const lastName = personalInfo.lastName || personalInfo.fullName.split(' ').slice(1).join(' ');
    for (const selector of lastNameFields) {
      if (this.fillTextField(selector, lastName)) {
        count++;
        break;
      }
    }

    // Email
    const emailFields = [
      'input[name*="email"]',
      'input[id*="email"]',
      'input[type="email"]',
    ];
    for (const selector of emailFields) {
      if (this.fillTextField(selector, personalInfo.email)) {
        count++;
        break;
      }
    }

    // Phone
    if (personalInfo.phone) {
      const phoneFields = [
        'input[name*="phone"]',
        'input[id*="phone"]',
        'input[name*="telephone"]',
      ];
      for (const selector of phoneFields) {
        if (this.fillTextField(selector, personalInfo.phone)) {
          count++;
          break;
        }
      }
    }

    // Address/Location
    if (personalInfo.location) {
      const locationFields = [
        'input[name*="city"]',
        'input[id*="city"]',
        'input[name*="location"]',
      ];
      for (const selector of locationFields) {
        if (this.fillTextField(selector, personalInfo.location)) {
          count++;
          break;
        }
      }
    }

    return count;
  }

  /**
   * Fill work experience step
   */
  private async fillExperienceStep(): Promise<number> {
    let count = 0;
    const { workExperience } = this.data!;

    if (!workExperience || workExperience.length === 0) {
      logger.warn('No work experience data provided');
      return 0;
    }

    // Taleo often has "Add" buttons for multiple experiences
    const addButton = document.querySelector('button[name*="add"], input[value*="Add"]') as HTMLElement;

    for (let i = 0; i < workExperience.length; i++) {
      const exp = workExperience[i];
      logger.debug(`Filling work experience ${i + 1}:`, exp.jobTitle);

      // Click "Add" if not first entry
      if (i > 0 && addButton) {
        addButton.click();
        await this.sleep(1000); // Wait for new form fields
      }

      // Job title
      const titleFields = [
        `input[name*="jobTitle"][${i}]`,
        `input[name*="position"][${i}]`,
        'input[name*="jobTitle"]:not([value])',
      ];
      for (const selector of titleFields) {
        if (this.fillTextField(selector, exp.jobTitle)) {
          count++;
          break;
        }
      }

      // Company
      const companyFields = [
        `input[name*="employer"][${i}]`,
        `input[name*="company"][${i}]`,
        'input[name*="employer"]:not([value])',
      ];
      for (const selector of companyFields) {
        if (this.fillTextField(selector, exp.companyName)) {
          count++;
          break;
        }
      }

      // Start date
      const startDate = this.formatDate(exp.startDate);
      if (this.fillTextField('input[name*="startDate"]:not([value])', startDate)) {
        count++;
      }

      // End date or current
      if (exp.isCurrent) {
        const currentCheckbox = document.querySelector('input[type="checkbox"][name*="current"]') as HTMLInputElement;
        if (currentCheckbox) {
          currentCheckbox.checked = true;
          count++;
        }
      } else if (exp.endDate) {
        const endDate = this.formatDate(exp.endDate);
        if (this.fillTextField('input[name*="endDate"]:not([value])', endDate)) {
          count++;
        }
      }
    }

    return count;
  }

  /**
   * Fill education step
   */
  private async fillEducationStep(): Promise<number> {
    let count = 0;
    const { education } = this.data!;

    if (!education || education.length === 0) {
      logger.warn('No education data provided');
      return 0;
    }

    const addButton = document.querySelector('button[name*="add"], input[value*="Add"]') as HTMLElement;

    for (let i = 0; i < education.length; i++) {
      const edu = education[i];
      logger.debug(`Filling education ${i + 1}:`, edu.institution);

      if (i > 0 && addButton) {
        addButton.click();
        await this.sleep(1000);
      }

      // School name
      const schoolFields = [
        'input[name*="school"]:not([value])',
        'input[name*="institution"]:not([value])',
      ];
      for (const selector of schoolFields) {
        if (this.fillTextField(selector, edu.institution)) {
          count++;
          break;
        }
      }

      // Degree
      if (edu.degree) {
        const degreeFields = [
          'input[name*="degree"]:not([value])',
          'select[name*="degree"]',
        ];
        for (const selector of degreeFields) {
          const element = document.querySelector(selector);
          if (element?.tagName === 'SELECT') {
            if (this.fillSelectField(selector, edu.degree)) {
              count++;
              break;
            }
          } else if (this.fillTextField(selector, edu.degree)) {
            count++;
            break;
          }
        }
      }

      // Field of study
      if (edu.fieldOfStudy) {
        if (this.fillTextField('input[name*="major"]:not([value])', edu.fieldOfStudy) ||
            this.fillTextField('input[name*="field"]:not([value])', edu.fieldOfStudy)) {
          count++;
        }
      }

      // Graduation date
      if (edu.endDate) {
        const gradDate = this.formatDate(edu.endDate);
        if (this.fillTextField('input[name*="graduation"]:not([value])', gradDate)) {
          count++;
        }
      }
    }

    return count;
  }

  /**
   * Fill questionnaire/custom questions step
   */
  private async fillQuestionnaireStep(): Promise<number> {
    let count = 0;

    try {
      // Look for all question fields
      const questions = document.querySelectorAll('.question, .questionRow');

      for (const question of Array.from(questions)) {
        const label = question.querySelector('label')?.textContent?.trim();
        if (!label) continue;

        const input = question.querySelector('input, textarea, select');
        if (input) {
          const filled = await this.fillCustomField(input as any, label);
          if (filled) count++;
        }
      }
    } catch (error) {
      logger.error('Questionnaire error:', error);
    }

    return count;
  }

  /**
   * Fill attachments step (resume upload)
   */
  private async fillAttachmentsStep(): Promise<boolean> {
    try {
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;

      if (!fileInput) {
        logger.warn('File input not found');
        return false;
      }

      logger.info('Resume upload field found (file would be uploaded here)');
      
      // TODO: Implement actual file upload
      return false;
    } catch (error) {
      logger.error('Attachments error:', error);
      return false;
    }
  }

  /**
   * Fill any visible fields (fallback)
   */
  private async fillVisibleFields(): Promise<number> {
    let count = 0;
    const { personalInfo } = this.data!;

    // Try common field patterns
    if (this.fillTextField('input[type="email"]', personalInfo.email)) count++;
    if (personalInfo.phone && this.fillTextField('input[type="tel"]', personalInfo.phone)) count++;
    
    return count;
  }

  /**
   * Fill a custom field
   */
  private async fillCustomField(
    field: HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement,
    label: string
  ): Promise<boolean> {
    const labelLower = label.toLowerCase();
    const { workExperience } = this.data!;

    // Work authorization
    if (labelLower.includes('authorized') && labelLower.includes('work')) {
      if (field.tagName === 'SELECT') {
        return this.fillSelectField(`#${field.id}`, 'Yes');
      }
      return this.fillRadioButton(field.name, 'yes');
    }

    // Sponsorship
    if (labelLower.includes('sponsorship')) {
      if (field.tagName === 'SELECT') {
        return this.fillSelectField(`#${field.id}`, 'No');
      }
      return this.fillRadioButton(field.name, 'no');
    }

    // Years of experience
    if (labelLower.includes('years') && labelLower.includes('experience')) {
      if (workExperience && workExperience.length > 0) {
        const totalYears = this.calculateTotalExperience(workExperience);
        return this.fillTextField(`#${field.id}`, String(totalYears));
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

  /**
   * Format date for Taleo (MM/DD/YYYY)
   */
  private formatDate(date: string): string {
    try {
      const d = new Date(date);
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      const year = d.getFullYear();
      return `${month}/${day}/${year}`;
    } catch {
      return date;
    }
  }
}
