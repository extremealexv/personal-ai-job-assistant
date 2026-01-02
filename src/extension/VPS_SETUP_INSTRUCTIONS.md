# VPS Setup Instructions for Browser Extension

## Step 1: Update package.json on VPS

Replace the content of `/home/jsappuser/personal-ai-job-assistant/src/extension/package.json` with:

```json
{
  "name": "ai-job-assistant-extension",
  "version": "0.1.0",
  "description": "Browser extension for automated job application form filling",
  "main": "dist/background/service-worker.js",
  "scripts": {
    "build": "webpack --mode production",
    "dev": "webpack --mode development --watch",
    "clean": "rimraf dist",
    "rebuild": "npm run clean && npm run build",
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "keywords": [
    "chrome-extension",
    "job-application",
    "autofill",
    "ats"
  ],
  "author": "",
  "license": "ISC",
  "devDependencies": {
    "@types/chrome": "^0.0.268",
    "copy-webpack-plugin": "^12.0.2",
    "rimraf": "^5.0.5",
    "ts-loader": "^9.5.1",
    "typescript": "^5.3.3",
    "webpack": "^5.90.0",
    "webpack-cli": "^5.1.4"
  }
}
```

**OR** run this command on VPS:

```bash
ssh jsappuser@vps-f7d6b34a.vps.ovh.net
cd /home/jsappuser/personal-ai-job-assistant/src/extension

cat > package.json << 'EOF'
{
  "name": "ai-job-assistant-extension",
  "version": "0.1.0",
  "description": "Browser extension for automated job application form filling",
  "main": "dist/background/service-worker.js",
  "scripts": {
    "build": "webpack --mode production",
    "dev": "webpack --mode development --watch",
    "clean": "rimraf dist",
    "rebuild": "npm run clean && npm run build",
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "keywords": [
    "chrome-extension",
    "job-application",
    "autofill",
    "ats"
  ],
  "author": "",
  "license": "ISC",
  "devDependencies": {
    "@types/chrome": "^0.0.268",
    "copy-webpack-plugin": "^12.0.2",
    "rimraf": "^5.0.5",
    "ts-loader": "^9.5.1",
    "typescript": "^5.3.3",
    "webpack": "^5.90.0",
    "webpack-cli": "^5.1.4"
  }
}
EOF
```

## Step 2: Install Missing Dependencies

On VPS, run:

```bash
cd /home/jsappuser/personal-ai-job-assistant/src/extension
npm install --save-dev copy-webpack-plugin rimraf
```

This installs:
- `copy-webpack-plugin`: Required by webpack.config.js to copy static files (manifest.json, HTML, CSS)
- `rimraf`: Cross-platform `rm -rf` for the clean script

## Step 3: Commit Local Files to Git

On your **local machine** (Windows), commit the extension foundation:

```powershell
cd C:\Users\alexa\OneDrive\Documents\personal-ai-job-assistant\personal-ai-job-assistant
git add src/extension/
git commit -m "feat(extension): add browser extension foundation (Part 1 of Phase 3)

- Add TypeScript configuration (tsconfig.json)
- Add Webpack bundling config (webpack.config.js)
- Add Manifest V3 configuration (manifest.json)
- Implement type definitions (160+ lines)
- Implement API client utility (160+ lines)
- Implement storage utility (140+ lines)
- Implement logger utility (60+ lines)
- Implement background service worker (170+ lines)
- Implement content script with platform detection (120+ lines)
- Create popup UI (HTML: 140 lines, CSS: 280 lines, TS: 240 lines)
- Add README and .gitignore
- Add SVG icon placeholder

Total: 12 core files, 1,600+ lines of code

Part of Issue #60 - Phase 3: Browser Extension - ATS Integration"
git push origin feature/browser-extension-60
```

## Step 4: Pull Changes on VPS

On VPS, pull the new files:

```bash
ssh jsappuser@vps-f7d6b34a.vps.ovh.net
cd /home/jsappuser/personal-ai-job-assistant
git pull origin feature/browser-extension-60
```

## Step 5: Build Extension

On VPS, build the extension:

```bash
cd /home/jsappuser/personal-ai-job-assistant/src/extension
npm run build
```

Expected output:
```
asset background/service-worker.js 123 KiB [emitted] (name: background)
asset content/content-script.js 45 KiB [emitted] (name: content)
asset popup/popup.js 67 KiB [emitted] (name: popup)
asset manifest.json 1.2 KiB [emitted]
asset popup/popup.html 2.3 KiB [emitted]
asset popup/popup.css 4.5 KiB [emitted]
webpack compiled successfully
```

## Step 6: Verify Build Output

Check that dist/ folder was created with all files:

```bash
ls -la dist/
```

Expected structure:
```
dist/
├── background/
│   └── service-worker.js
├── content/
│   └── content-script.js
├── popup/
│   ├── popup.js
│   ├── popup.html
│   └── popup.css
├── icons/
│   └── icon-128.svg
└── manifest.json
```

## Step 7: Transfer dist/ Folder to Local Machine (Optional)

If you want to test the extension on your local Chrome:

**Option A: Using SCP (PowerShell on Windows)**
```powershell
scp -r jsappuser@vps-f7d6b34a.vps.ovh.net:/home/jsappuser/personal-ai-job-assistant/src/extension/dist C:\Users\alexa\OneDrive\Documents\personal-ai-job-assistant\personal-ai-job-assistant\src\extension\
```

**Option B: Using Git (if dist/ is not ignored)**
- On VPS: `git add -f dist/ && git commit -m "temp: add dist for testing" && git push`
- On local: `git pull`
- After testing: `git rm -r dist/ && git commit -m "remove dist" && git push`

## Step 8: Test Extension in Chrome

1. Open Chrome and navigate to `chrome://extensions`
2. Enable "Developer mode" (toggle in top-right)
3. Click "Load unpacked"
4. Select the `dist/` folder
5. Extension should load with icon in toolbar

## Step 9: Test Basic Functionality

1. Click extension icon
2. You should see the login screen
3. Try entering test credentials (backend must be running)
4. Navigate to a test ATS page (e.g., any Workday jobs site)
5. Extension should detect platform (check content script console logs)

## Troubleshooting

### Build Errors

**Error: Cannot find module 'copy-webpack-plugin'**
```bash
npm install --save-dev copy-webpack-plugin
```

**Error: Cannot find module 'typescript'**
```bash
npm install --save-dev typescript ts-loader
```

### Extension Loading Errors

**Error: "Manifest version 2 is deprecated"**
- We're using V3, ignore this if you see it elsewhere

**Error: "Could not load icon"**
- Icons are optional for development, extension will work without them
- SVG icon placeholder is provided in public/icons/

**Error: "Failed to load background script"**
- Check browser console: `chrome://extensions` → Details → "Inspect views: service worker"
- Look for TypeScript compilation errors

### Runtime Errors

**Content script not injecting**
- Check host permissions in manifest.json
- Verify you're on a supported ATS domain
- Check page console for errors

**API client failing**
- Backend must be running on http://localhost:8000
- Check CORS settings in backend
- Verify authentication token storage

## Next Steps After Successful Build

1. ✅ **Part 1 Complete**: Extension foundation built and tested
2. 🚧 **Part 2 Next**: Implement ATS strategy pattern
   - Create base-strategy.ts
   - Implement workday-strategy.ts
   - Implement greenhouse-strategy.ts
   - Implement lever-strategy.ts
   - Implement taleo-strategy.ts
3. 🚧 **Part 3**: Implement autofill logic
4. 🚧 **Part 4**: Testing and QA
5. 🚧 **Part 5**: UI polish and documentation

## Questions?

If you encounter issues during VPS setup or build, share:
1. The exact error message
2. Which step you're on
3. Output of `npm list` (to verify dependencies)
