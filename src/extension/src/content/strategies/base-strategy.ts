/**
 * Base Strategy for ATS Platform Autofill
 * 
 * This abstract class defines the interface that all ATS-specific strategies must implement.
 * It provides common utility methods for DOM manipulation and form filling.
 */

import type { ApplicationData, AutofillResult, ATSStrategy } from '../../types';
import { logger } from '../../utils/logger';

export abstract class BaseATSStrategy implements ATSStrategy {
  protected data: ApplicationData | null = null;
  protected startTime: number = 0;

  /**
   * Detect if current page is this ATS platform
   * Must be implemented by each platform-specific strategy
   */
  abstract detect(): boolean;

  /**
   * Perform autofill for this platform
   * Must be implemented by each platform-specific strategy
   */
  abstract autofill(data: ApplicationData): Promise<AutofillResult>;

  /**
   * Get platform name
   * Must be implemented by each platform-specific strategy
   */
  abstract getPlatformName(): string;

  /**
   * Utility: Fill text input field
   */
  protected fillTextField(selector: string, value: string): boolean {
    try {
      const element = document.querySelector(selector) as HTMLInputElement | HTMLTextAreaElement;
      if (!element) {
        logger.warn(`Text field not found: ${selector}`);
        return false;
      }

      // Set value and trigger events
      element.value = value;
      element.dispatchEvent(new Event('input', { bubbles: true }));
      element.dispatchEvent(new Event('change', { bubbles: true }));
      element.dispatchEvent(new Event('blur', { bubbles: true }));

      logger.debug(`Filled text field: ${selector} = ${value}`);
      return true;
    } catch (error) {
      logger.error(`Error filling text field ${selector}:`, error);
      return false;
    }
  }

  /**
   * Utility: Fill select/dropdown field
   */
  protected fillSelectField(selector: string, value: string): boolean {
    try {
      const element = document.querySelector(selector) as HTMLSelectElement;
      if (!element) {
        logger.warn(`Select field not found: ${selector}`);
        return false;
      }

      // Try exact match first
      const exactOption = Array.from(element.options).find(
        (opt) => opt.value === value || opt.text === value
      );

      if (exactOption) {
        element.value = exactOption.value;
      } else {
        // Try partial match
        const partialOption = Array.from(element.options).find(
          (opt) => opt.text.toLowerCase().includes(value.toLowerCase())
        );

        if (partialOption) {
          element.value = partialOption.value;
        } else {
          logger.warn(`No matching option found for: ${selector} = ${value}`);
          return false;
        }
      }

      element.dispatchEvent(new Event('change', { bubbles: true }));
      logger.debug(`Selected option: ${selector} = ${value}`);
      return true;
    } catch (error) {
      logger.error(`Error filling select field ${selector}:`, error);
      return false;
    }
  }

  /**
   * Utility: Fill radio button
   */
  protected fillRadioButton(name: string, value: string): boolean {
    try {
      const radios = document.querySelectorAll(`input[type="radio"][name="${name}"]`);
      if (radios.length === 0) {
        logger.warn(`Radio buttons not found: ${name}`);
        return false;
      }

      for (const radio of Array.from(radios)) {
        const radioElement = radio as HTMLInputElement;
        if (radioElement.value === value || radioElement.getAttribute('data-label') === value) {
          radioElement.checked = true;
          radioElement.dispatchEvent(new Event('change', { bubbles: true }));
          logger.debug(`Selected radio: ${name} = ${value}`);
          return true;
        }
      }

      logger.warn(`No matching radio option: ${name} = ${value}`);
      return false;
    } catch (error) {
      logger.error(`Error filling radio button ${name}:`, error);
      return false;
    }
  }

  /**
   * Utility: Fill checkbox
   */
  protected fillCheckbox(selector: string, checked: boolean): boolean {
    try {
      const element = document.querySelector(selector) as HTMLInputElement;
      if (!element) {
        logger.warn(`Checkbox not found: ${selector}`);
        return false;
      }

      if (element.checked !== checked) {
        element.checked = checked;
        element.dispatchEvent(new Event('change', { bubbles: true }));
        logger.debug(`Set checkbox: ${selector} = ${checked}`);
      }

      return true;
    } catch (error) {
      logger.error(`Error filling checkbox ${selector}:`, error);
      return false;
    }
  }

  /**
   * Utility: Upload file
   */
  protected async uploadFile(selector: string, fileData: Blob, fileName: string): Promise<boolean> {
    try {
      const element = document.querySelector(selector) as HTMLInputElement;
      if (!element || element.type !== 'file') {
        logger.warn(`File input not found: ${selector}`);
        return false;
      }

      // Create File object from Blob
      const file = new File([fileData], fileName, { type: fileData.type });
      
      // Create DataTransfer to set files
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      element.files = dataTransfer.files;

      element.dispatchEvent(new Event('change', { bubbles: true }));
      logger.debug(`Uploaded file: ${selector} = ${fileName}`);
      return true;
    } catch (error) {
      logger.error(`Error uploading file ${selector}:`, error);
      return false;
    }
  }

  /**
   * Utility: Wait for element to appear
   */
  protected async waitForElement(
    selector: string,
    timeout: number = 5000
  ): Promise<Element | null> {
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      const element = document.querySelector(selector);
      if (element) {
        logger.debug(`Element found: ${selector}`);
        return element;
      }
      await this.sleep(100);
    }

    logger.warn(`Element not found after ${timeout}ms: ${selector}`);
    return null;
  }

  /**
   * Utility: Wait for multiple elements
   */
  protected async waitForElements(
    selector: string,
    minCount: number = 1,
    timeout: number = 5000
  ): Promise<NodeListOf<Element> | null> {
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      const elements = document.querySelectorAll(selector);
      if (elements.length >= minCount) {
        logger.debug(`Found ${elements.length} elements: ${selector}`);
        return elements;
      }
      await this.sleep(100);
    }

    logger.warn(`Elements not found after ${timeout}ms: ${selector} (min: ${minCount})`);
    return null;
  }

  /**
   * Utility: Click element
   */
  protected clickElement(selector: string): boolean {
    try {
      const element = document.querySelector(selector) as HTMLElement;
      if (!element) {
        logger.warn(`Element not found: ${selector}`);
        return false;
      }

      element.click();
      logger.debug(`Clicked element: ${selector}`);
      return true;
    } catch (error) {
      logger.error(`Error clicking element ${selector}:`, error);
      return false;
    }
  }

  /**
   * Utility: Scroll to element
   */
  protected scrollToElement(selector: string): boolean {
    try {
      const element = document.querySelector(selector) as HTMLElement;
      if (!element) {
        logger.warn(`Element not found: ${selector}`);
        return false;
      }

      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      logger.debug(`Scrolled to element: ${selector}`);
      return true;
    } catch (error) {
      logger.error(`Error scrolling to element ${selector}:`, error);
      return false;
    }
  }

  /**
   * Utility: Sleep/delay
   */
  protected sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Utility: Get elapsed time since autofill started
   */
  protected getElapsedTime(): number {
    return Date.now() - this.startTime;
  }

  /**
   * Utility: Create success result
   */
  protected createSuccessResult(fieldsFilledCount: number): AutofillResult {
    return {
      success: true,
      platform: this.getPlatformName(),
      fieldsFilledCount,
      duration: this.getElapsedTime(),
    };
  }

  /**
   * Utility: Create error result
   */
  protected createErrorResult(message: string, error?: any): AutofillResult {
    return {
      success: false,
      platform: this.getPlatformName(),
      fieldsFilledCount: 0,
      duration: this.getElapsedTime(),
      message,
      errors: error ? [String(error)] : undefined,
    };
  }
}
