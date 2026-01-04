/**
 * Workday ATS Strategy
 * 
 * Handles autofill for Workday application forms.
 * Workday is one of the most common ATS platforms used by large enterprises.
 * 
 * Detection: URL contains "myworkdayjobs.com" or specific Workday DOM classes
 * Form Structure: Multi-section forms with standardized field names
 */

import type { ApplicationData, AutofillResult } from '../../types';
import { BaseATSStrategy } from './base-strategy';
import { logger } from '../../utils/logger';

export class WorkdayStrategy extends BaseATSStrategy {
  /**
   * Detect if current page is Workday
   */
  detect(): boolean {
    // Check URL for any Workday domain
    const hostname = window.location.hostname.toLowerCase();
    if (hostname.includes('myworkdayjobs.com') || 
        hostname.includes('myworkdaysite.com') ||
        hostname.includes('workday.com')) {
      logger.info('Workday detected via URL:', hostname);
      return true;
    }

    // Check for Workday-specific DOM elements
    const workdayElements = [
      '[data-automation-id="formField-name"]',
      '[data-automation-id="formField-email"]',
      '.css-k008qs', // Workday form container class (may vary)
      '[data-uxi-widget-type="formField"]',
      '[data-automation-id*="formField"]', // Any Workday form field
    ];

    const detected = workdayElements.some((selector) => document.querySelector(selector) !== null);
    if (detected) {
      logger.info('Workday detected via DOM elements');
    }
    return detected;
  }

  /**
   * Get platform name
   */
  getPlatformName(): string {
    return 'workday';
  }

  /**
   * Perform autofill for Workday
   */
  async autofill(data: ApplicationData): Promise<AutofillResult> {
    this.data = data;
    this.startTime = Date.now();
    let fieldsFilledCount = 0;

    try {
      logger.info('Starting Workday autofill...');

      // Wait for any Workday form field to appear (flexible detection)
      const formSelectors = [
        '[data-automation-id*="formField"]',
        'input[name*="firstName"]',
        'input[name*="lastName"]',
        '.css-k008qs',
        '[data-uxi-widget-type="formField"]',
      ];
      
      let formFound = false;
      for (const selector of formSelectors) {
        const element = await this.waitForElement(selector, 2000);
        if (element) {
          logger.info('Workday form detected with selector:', selector);
          formFound = true;
          break;
        }
      }
      
      if (!formFound) {
        return this.createErrorResult('Workday form not found - no form fields detected');
      }

      // Section 1: Personal Information
      logger.info('Filling personal information...');
      fieldsFilledCount += await this.fillPersonalInfo();

      // Section 2: Contact Information
      logger.info('Filling contact information...');
      fieldsFilledCount += await this.fillContactInfo();

      // Section 3: Work Experience
      logger.info('Filling work experience...');
      fieldsFilledCount += await this.fillWorkExperience();

      // Section 4: Education
      logger.info('Filling education...');
      fieldsFilledCount += await this.fillEducation();

      // Section 5: Resume Upload
      logger.info('Uploading resume...');
      const resumeUploaded = await this.uploadResume();
      if (resumeUploaded) fieldsFilledCount++;

      // Section 6: Cover Letter (if available)
      if (data.coverLetter) {
        logger.info('Handling cover letter...');
        const coverLetterHandled = await this.handleCoverLetter();
        if (coverLetterHandled) fieldsFilledCount++;
      }

      logger.info(`Workday autofill complete: ${fieldsFilledCount} fields filled`);
      return this.createSuccessResult(fieldsFilledCount);
    } catch (error) {
      logger.error('Workday autofill error:', error);
      return this.createErrorResult('Autofill failed', error);
    }
  }

  /**
   * Fill personal information section
   */
  private async fillPersonalInfo(): Promise<number> {
    let count = 0;
    const { personalInfo } = this.data!;

    // Full name (may be split into first/last or combined)
    if (this.fillTextField('[data-automation-id="formField-name"]', personalInfo.fullName)) {
      count++;
    }

    // First name
    if (this.fillTextField('[data-automation-id="formField-firstName"]', personalInfo.firstName || '')) {
      count++;
    }

    // Last name
    if (this.fillTextField('[data-automation-id="formField-lastName"]', personalInfo.lastName || '')) {
      count++;
    }

    // Location/City
    if (personalInfo.location) {
      if (this.fillTextField('[data-automation-id="formField-location"]', personalInfo.location)) {
        count++;
      }
      if (this.fillTextField('[data-automation-id="formField-city"]', personalInfo.location)) {
        count++;
      }
    }

    return count;
  }

  /**
   * Fill contact information section
   */
  private async fillContactInfo(): Promise<number> {
    let count = 0;
    const { personalInfo } = this.data!;

    // Email
    if (this.fillTextField('[data-automation-id="formField-email"]', personalInfo.email)) {
      count++;
    }
    if (this.fillTextField('[data-automation-id="emailAddress"]', personalInfo.email)) {
      count++;
    }

    // Phone
    if (personalInfo.phone) {
      if (this.fillTextField('[data-automation-id="formField-phone"]', personalInfo.phone)) {
        count++;
      }
      if (this.fillTextField('[data-automation-id="phoneNumber"]', personalInfo.phone)) {
        count++;
      }
    }

    // LinkedIn
    if (personalInfo.linkedinUrl) {
      if (this.fillTextField('[data-automation-id="formField-linkedin"]', personalInfo.linkedinUrl)) {
        count++;
      }
    }

    // Website/Portfolio
    if (personalInfo.portfolioUrl) {
      if (this.fillTextField('[data-automation-id="formField-website"]', personalInfo.portfolioUrl)) {
        count++;
      }
    }

    return count;
  }

  /**
   * Fill work experience section
   */
  private async fillWorkExperience(): Promise<number> {
    let count = 0;
    const { workExperience } = this.data!;

    if (!workExperience || workExperience.length === 0) {
      logger.warn('No work experience data provided');
      return 0;
    }

    // Workday typically has "Add Work Experience" buttons
    const addExperienceButton = document.querySelector(
      '[data-automation-id="addItemButton-work"]'
    ) as HTMLElement;

    for (let i = 0; i < workExperience.length; i++) {
      const exp = workExperience[i];
      logger.debug(`Filling work experience ${i + 1}:`, exp.jobTitle);

      // Click "Add" button if not first entry
      if (i > 0 && addExperienceButton) {
        addExperienceButton.click();
        await this.sleep(500); // Wait for form to appear
      }

      const prefix = `[data-automation-id="work-${i}"]`;

      // Job title
      if (this.fillTextField(`${prefix}-title`, exp.jobTitle)) count++;

      // Company
      if (this.fillTextField(`${prefix}-company`, exp.companyName)) count++;

      // Start date (may need formatting)
      const startDate = this.formatDate(exp.startDate);
      if (this.fillTextField(`${prefix}-startDate`, startDate)) count++;

      // End date or "Current"
      if (exp.isCurrent) {
        if (this.fillCheckbox(`${prefix}-currentJob`, true)) count++;
      } else if (exp.endDate) {
        const endDate = this.formatDate(exp.endDate);
        if (this.fillTextField(`${prefix}-endDate`, endDate)) count++;
      }

      // Description
      if (exp.description) {
        if (this.fillTextField(`${prefix}-description`, exp.description)) count++;
      }
    }

    return count;
  }

  /**
   * Fill education section
   */
  private async fillEducation(): Promise<number> {
    let count = 0;
    const { education } = this.data!;

    if (!education || education.length === 0) {
      logger.warn('No education data provided');
      return 0;
    }

    const addEducationButton = document.querySelector(
      '[data-automation-id="addItemButton-education"]'
    ) as HTMLElement;

    for (let i = 0; i < education.length; i++) {
      const edu = education[i];
      logger.debug(`Filling education ${i + 1}:`, edu.institution);

      // Click "Add" button if not first entry
      if (i > 0 && addEducationButton) {
        addEducationButton.click();
        await this.sleep(500);
      }

      const prefix = `[data-automation-id="education-${i}"]`;

      // Institution
      if (this.fillTextField(`${prefix}-school`, edu.institution)) count++;

      // Degree
      if (edu.degree) {
        if (this.fillTextField(`${prefix}-degree`, edu.degree)) count++;
      }

      // Field of study
      if (edu.fieldOfStudy) {
        if (this.fillTextField(`${prefix}-field`, edu.fieldOfStudy)) count++;
      }

      // Graduation date
      if (edu.endDate) {
        const gradDate = this.formatDate(edu.endDate);
        if (this.fillTextField(`${prefix}-graduationDate`, gradDate)) count++;
      }

      // GPA (if provided)
      if (edu.gpa) {
        if (this.fillTextField(`${prefix}-gpa`, String(edu.gpa))) count++;
      }
    }

    return count;
  }

  /**
   * Upload resume file
   */
  private async uploadResume(): Promise<boolean> {
    try {
      // Workday typically has a file upload widget
      const fileInput = document.querySelector(
        '[data-automation-id="file-upload-input-ref"]'
      ) as HTMLInputElement;

      if (!fileInput) {
        logger.warn('Resume file input not found');
        return false;
      }

      // In real implementation, we would fetch the resume file from the backend
      // For now, we'll just log that we found the input
      logger.info('Resume upload field found (file would be uploaded here)');
      
      // TODO: Implement actual file upload once backend integration is complete
      // const resumeBlob = await this.fetchResumeFile();
      // return await this.uploadFile('[data-automation-id="file-upload-input-ref"]', resumeBlob, 'resume.pdf');

      return false;
    } catch (error) {
      logger.error('Resume upload error:', error);
      return false;
    }
  }

  /**
   * Handle cover letter (upload or paste)
   */
  private async handleCoverLetter(): Promise<boolean> {
    try {
      // Check for cover letter text area
      const textArea = document.querySelector(
        '[data-automation-id="formField-coverLetter"]'
      ) as HTMLTextAreaElement;

      if (textArea && this.data!.coverLetter) {
        return this.fillTextField(
          '[data-automation-id="formField-coverLetter"]',
          this.data!.coverLetter
        );
      }

      // Check for cover letter file upload
      const fileInput = document.querySelector(
        '[data-automation-id="coverLetter-upload"]'
      ) as HTMLInputElement;

      if (fileInput) {
        logger.info('Cover letter upload field found');
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
   * Format date for Workday (MM/DD/YYYY)
   */
  private formatDate(date: string): string {
    try {
      const d = new Date(date);
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      const year = d.getFullYear();
      return `${month}/${day}/${year}`;
    } catch {
      return date; // Return original if parsing fails
    }
  }
}
