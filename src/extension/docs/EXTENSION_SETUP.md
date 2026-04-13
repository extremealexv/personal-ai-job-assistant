# Extension Setup Guide

## Working with APIs and CORS

To successfully communicate with the Personal AI Job Assistant backend APIs, the browser extension assumes the backend services are running and accessible.

### Problem
By default, the backend limits CORS to specific origins (e.g., `http://localhost:3000`). Since the extension communicates dynamically (either from `chrome-extension://<extension-id>` via the background worker, or across multiple ATS domains like `https://boards.greenhouse.io` via the content scripts), API requests may be blocked by CORS policies.

### Backend Configuration Solution
You must configure the central `CORS_ORIGINS` environment variable in the backend's `.env` to encompass standard ATS environments or set a wildcard in development.

Example `.env` adjustment on your backend:
```env
# Allow extension Origin + standard AST platforms
CORS_ORIGINS="http://localhost:3000,http://localhost:5173,chrome-extension://*,.myworkdayjobs.com,.greenhouse.io,.lever.co,.taleo.net"
```

If you face preflight request blockers (`OPTIONS` failing):
1. **Extension Mode (Optimal)**: Refactor your extension API calls to ONLY originate from `serviceWorker.ts` using `chrome.runtime.sendMessage`, routing all external traffic cleanly through the `chrome-extension://` origin.
2. Ensure `allow_credentials=True` is verified in your `main.py` CORS deployment.
