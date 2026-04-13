import { BaseATSStrategy, UserPayload } from './BaseATSStrategy';

export class TaleoStrategy extends BaseATSStrategy {
    detect(url: string): boolean {
        return url.includes('taleo.net');
    }

    getFieldMap(): Record<keyof UserPayload, string> {
        return {
            firstName: 'input[name*="FirstName"]',
            lastName: 'input[name*="LastName"]',
            email: 'input[name*="EmailAddress"]',
            phone: 'input[name*="PhoneNumber"]',
            linkedIn: 'input[name*="LinkedIn"]',
            github: 'input[name*="GitHub"]',
            portfolio: 'input[name*="Website"]'
        };
    }
}
