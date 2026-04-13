import puppeteer from 'puppeteer';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

(async () => {
    const extensionPath = path.resolve(__dirname, 'dist');

    console.log(`Loading extension from ${extensionPath}`);

    const browser = await puppeteer.launch({
        headless: "new",
        args: [
            `--disable-extensions-except=${extensionPath}`,
            `--load-extension=${extensionPath}`,
            '--no-sandbox',
            '--disable-setuid-sandbox'
        ],
    });

    console.log("Browser loaded with extension.");
    
    const page = await browser.newPage();
    
    let contentScriptLoaded = false;
    
    page.on('console', msg => {
        const text = msg.text();
        console.log(`[PAGE LOG] ${text}`);
        if (text.includes("Personal AI Job Assistant logic loaded") || text.includes("Scanning ATS page")) {
            contentScriptLoaded = true;
        }
    });

    console.log("Navigating to https://jobs.lever.co/...");
    await page.goto("https://jobs.lever.co/", { waitUntil: 'networkidle2' });

    console.log("Navigation complete. Waiting for content script marker in the DOM...");
    
    try {
        await page.waitForSelector('#ai-job-assistant-marker', { timeout: 10000 });
        console.log("SUCCESS: Content script was injected and executed on an ATS site!");
        await browser.close();
        process.exit(0);
    } catch (e) {
        console.error("FAILURE: Content script DOM marker was not found.");
        await browser.close();
        process.exit(1);
    }
})();
