export interface WorkExperience {
    company: string;
    title: string;
    startDate: string;
    endDate?: string;
    description: string;
}

export interface Education {
    school: string;
    degree: string;
    field: string;
    graduationDate: string;
    gpa?: string;
}

export interface Base64File {
    name: string;
    type: string;
    content: string; // base64 string without data-uri prefix
}

export interface UserPayload {
    firstName?: string;
    lastName?: string;
    email?: string;
    phone?: string;
    linkedIn?: string;
    github?: string;
    portfolio?: string;
    experience?: WorkExperience[];
    education?: Education[];
    resumeFile?: Base64File;
    coverLetterFile?: Base64File;
    [key: string]: any;
}

export abstract class BaseATSStrategy {
    /**
     * Determines whether the current page is an instance of this ATS.
     */
    abstract detect(url: string): boolean;

    /**
     * Retrieves the specific CSS selectors for standard auto-fill properties.
     */
    abstract getFieldMap(): Record<keyof UserPayload, string>;

    /**
     * Base implementation for simulating user input into HTML form fields.
     */
    getFileMap(): Record<"resumeFile" | "coverLetterFile", string | null> {
        return {
            resumeFile: 'input[type="file"][name*="resume"], input[type="file"][id*="resume"]',
            coverLetterFile: 'input[type="file"][name*="cover"], input[type="file"][id*="cover"]'
        };
    }

    async injectPayload(payload: UserPayload): Promise<void> {
        const fieldMap = this.getFieldMap();
        for (const [key, selector] of Object.entries(fieldMap)) {
            const value = payload[key];
            if (!value || typeof value !== 'string') continue;

            let element = document.querySelector(selector) as HTMLInputElement;
            if (!element) {
                element = this.fuzzyMatch(key) as HTMLInputElement;
            }

            if (element) {
                this.setNativeValue(element, value);
            }
        }
        
        const fileMap = this.getFileMap();
        if (fileMap.resumeFile) {
            await this.injectFile(fileMap.resumeFile, payload.resumeFile);
        }
        if (fileMap.coverLetterFile) {
            await this.injectFile(fileMap.coverLetterFile, payload.coverLetterFile);
        }
        
        await this.injectArrays(payload);
    }

    protected async injectFile(selector: string, fileData: Base64File | undefined) {
        if (!fileData) return;
        const input = document.querySelector(selector) as HTMLInputElement;
        if (!input || input.type !== 'file') return;

        try {
            const byteCharacters = atob(fileData.content);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], { type: fileData.type });
            const file = new File([blob], fileData.name, { type: fileData.type });
            
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            input.files = dataTransfer.files;

            const event = new Event('change', { bubbles: true });
            input.dispatchEvent(event);
            console.log(`[BaseATSStrategy] Successfully injected file buffer into ${selector}`);
        } catch (e) {
            console.error(`[BaseATSStrategy] File parsing error injection failed: ${e}`);
        }
    }

    /**
     * Override this in specific Providers to iterate through specialized 'Add Experience' loops.
     */
    async injectArrays(_payload: UserPayload): Promise<void> {
        // Default does nothing
    }

    /**
     * Fallback to dynamically identify inputs based on semantic attribute analysis
     */
    protected fuzzyMatch(fieldKey: string): HTMLInputElement | HTMLTextAreaElement | null {
        const inputs = Array.from(document.querySelectorAll('input:not([type="hidden"]), textarea')) as (HTMLInputElement | HTMLTextAreaElement)[];
        
        const matchers: Record<string, string[]> = {
            firstName: ['first', 'fname'],
            lastName: ['last', 'lname'],
            email: ['email', 'e-mail'],
            phone: ['phone', 'mobile', 'cell', 'tel'],
            linkedIn: ['linkedin'],
            github: ['github'],
            portfolio: ['portfolio', 'website', 'url']
        };

        const targetKeywords = matchers[fieldKey] || [];
        
        for (const input of inputs) {
            const attributes = [
                input.id, 
                input.name, 
                input.placeholder, 
                input.getAttribute('aria-label')
            ].map(s => (s || '').toLowerCase());
            
            if (targetKeywords.some(keyword => attributes.some(attr => attr.includes(keyword)))) {
                return input;
            }
        }
        return null;
    }

    /**
     * Safely bypasses React's virtual DOM input controllers by getting the native input setter
     * and dispatching a synthetic javascript event.
     */
    protected setNativeValue(element: HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement, value: string) {
        let lastValue = element.value;
        element.value = value;
        const event = new Event('input', { bubbles: true });
        
        // React 15+ hack
        const tracker = (element as any)._valueTracker;
        if (tracker) {
            tracker.setValue(lastValue);
        }
        
        element.dispatchEvent(event);
        element.dispatchEvent(new Event('change', { bubbles: true }));
    }
}
