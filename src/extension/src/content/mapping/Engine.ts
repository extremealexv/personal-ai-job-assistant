import { BaseATSStrategy, UserPayload } from '../ats/BaseATSStrategy';
import { LeverStrategy } from '../ats/LeverStrategy';
import { GreenhouseStrategy } from '../ats/GreenhouseStrategy';
import { WorkdayStrategy } from '../ats/WorkdayStrategy';
import { TaleoStrategy } from '../ats/TaleoStrategy';

export class MappingEngine {
    private strategies: BaseATSStrategy[] = [
        new LeverStrategy(),
        new GreenhouseStrategy(),
        new WorkdayStrategy(),
        new TaleoStrategy(),
    ];

    detectStrategy(): BaseATSStrategy | null {
        const url = window.location.href;
        for (const strategy of this.strategies) {
            if (strategy.detect(url)) {
                return strategy;
            }
        }
        return null;
    }

    executeFill(payload: UserPayload): boolean {
        const strategy = this.detectStrategy();
        if (!strategy) {
            console.warn("No compatible ATS strategy detected for this URL.");
            return false;
        }

        console.log(`Executing mapping with identified strategy: ${strategy.constructor.name}`);
        strategy.injectPayload(payload);
        return true;
    }

    /**
     * Initializes a MutationObserver to handle Single Page Applications (SPAs).
     * If the DOM reconstructs significantly, re-apply payload.
     */
    observeSPAForms(payload: UserPayload) {
        let timeout: any = null;
        const observer = new MutationObserver((mutations) => {
            // Basic debounce
            if (timeout) clearTimeout(timeout);
            timeout = setTimeout(() => {
                const buttons = Array.from(document.querySelectorAll('button, a'));
                const hasNav = buttons.some(b => 
                    b.textContent?.includes('Next') || 
                    b.textContent?.includes('Continue')
                );
                
                if (hasNav || mutations.length > 50) {
                    // Attempt to backfill newly painted DOM structures
                    this.executeFill(payload);
                }
            }, 1000);
        });

        observer.observe(document.body, { childList: true, subtree: true });
        console.log("[MappingEngine] SPA DOM Observer attached.");
        return observer;
    }
}
