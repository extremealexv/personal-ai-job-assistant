import { BaseATSStrategy, UserPayload } from './BaseATSStrategy';

export class LeverStrategy extends BaseATSStrategy {
    detect(url: string): boolean {
        return url.includes('jobs.lever.co');
    }

    getFieldMap(): Record<keyof UserPayload, string> {
        return {
            firstName: 'input[name="filter-first-name"], input[name="name"]', // Lever sometimes merges names
            lastName: 'input[name="filter-last-name"]',
            email: 'input[name="email"]',
            phone: 'input[name="phone"]',
            linkedIn: 'input[name="urls[LinkedIn]"]',
            github: 'input[name="urls[GitHub]"]',
            portfolio: 'input[name="urls[Portfolio]"]'
        };
    }

    async injectArrays(payload: UserPayload): Promise<void> {
        if (!payload.experience) return;
        
        payload.experience.forEach((exp, index) => {
            const companyInput = document.querySelector(`input[name="cards[${index}][org]"]`) as HTMLInputElement;
            const titleInput = document.querySelector(`input[name="cards[${index}][title]"]`) as HTMLInputElement;
            const descInput = document.querySelector(`textarea[name="cards[${index}][summary]"]`) as HTMLTextAreaElement;
            
            if (companyInput) this.setNativeValue(companyInput, exp.company);
            if (titleInput) this.setNativeValue(titleInput, exp.title);
            if (descInput) this.setNativeValue(descInput, exp.description);
        });
    }
}
