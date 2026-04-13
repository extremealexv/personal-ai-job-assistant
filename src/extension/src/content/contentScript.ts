import { MappingEngine } from './mapping/Engine';
import { UserPayload } from './ats/BaseATSStrategy';

console.log("Personal AI Job Assistant logic loaded on ATS target page.");

function init() {
    console.log("Scanning ATS page for identifiable form variants...");
    
    const engine = new MappingEngine();
    const strategy = engine.detectStrategy();

    // Only inject UI if this is a supported ATS domain
    if (strategy) {
        const btn = document.createElement("button");
        btn.id = "ai-job-assistant-fab";
        btn.innerText = "🤖 Autofill Job";
        
        Object.assign(btn.style, {
            position: 'fixed',
            bottom: '24px',
            right: '24px',
            backgroundColor: '#4F46E5',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            padding: '12px 20px',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: 'pointer',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            zIndex: '999999'
        });
        
        btn.addEventListener('click', () => {
            console.log(`[AI Job Assistant] Detected ${strategy.constructor.name}! Populating data...`);
            
            // Mock payload for immediate verification
            // This will be replaced with real API fetching in the final backend tying.
            const mockPayload: UserPayload = {
                firstName: "Alex",
                lastName: "Extreme",
                email: "alex@extreme.demo",
                phone: "123-456-7890",
                linkedIn: "https://linkedin.com/in/extremealexv",
                github: "https://github.com/extremealexv",
                portfolio: "https://extremealexv.dev"
            };
            engine.executeFill(mockPayload);
        });
        
        document.body.appendChild(btn);
    }
}

if (document.readyState === 'complete' || document.readyState === 'interactive') {
    init();
} else {
    window.addEventListener('DOMContentLoaded', init);
}
