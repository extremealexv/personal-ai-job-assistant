import { BaseATSStrategy, UserPayload } from './BaseATSStrategy';

export class GreenhouseStrategy extends BaseATSStrategy {
    detect(url: string): boolean {
        return url.includes('boards.greenhouse.io') || url.includes('.greenhouse.io');
    }

    getFieldMap(): Record<keyof UserPayload, string> {
        return {
            firstName: 'input[id="first_name"]',
            lastName: 'input[id="last_name"]',
            email: 'input[id="email"]',
            phone: 'input[id="phone"]',
            linkedIn: 'input[autocomplete="custom-question-linkedin-profile"]', // Often customized
            github: 'input[autocomplete="custom-question-github"]',
            portfolio: 'input[autocomplete="custom-question-portfolio"]'
        };
    }
}
