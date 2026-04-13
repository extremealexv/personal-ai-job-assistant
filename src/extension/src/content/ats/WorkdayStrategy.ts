import { BaseATSStrategy, UserPayload } from './BaseATSStrategy';

export class WorkdayStrategy extends BaseATSStrategy {
    detect(url: string): boolean {
        return url.includes('myworkdayjobs.com');
    }

    getFieldMap(): Record<keyof UserPayload, string> {
        // Workday uses generic data-automation-id tags extensively
        return {
            firstName: 'input[data-automation-id="legalNameSection_firstName"]',
            lastName: 'input[data-automation-id="legalNameSection_lastName"]',
            email: 'input[data-automation-id="email"]',
            phone: 'input[data-automation-id="phoneDeviceData"]',
            linkedIn: 'input[data-automation-id="linkedin"]',
            github: 'input[data-automation-id="github"]',
            portfolio: 'input[data-automation-id="website"]'
        };
    }
}
