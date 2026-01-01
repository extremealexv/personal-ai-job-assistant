# 🚀 Quick Start: Google Gemini Setup (FREE)

## Step 1: Get Your FREE Gemini API Key

1. Go to **Google AI Studio**: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy your API key (starts with `AIza...`)

**Note**: Gemini Pro is **100% FREE** with generous limits:
- ✅ 60 requests per minute
- ✅ No expiration date
- ✅ No credit card required

## Step 2: Update Your .env File

On your VPS:

```bash
cd ~/personal-ai-job-assistant/src/backend
nano .env
```

Add these lines to your `.env`:

```bash
# AI Provider Configuration
AI_PROVIDER=gemini

# Google Gemini API Key (FREE)
GEMINI_API_KEY=AIza_YOUR_KEY_HERE
GEMINI_MODEL=gemini-pro
GEMINI_MAX_TOKENS=4000
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_RETRIES=3
```

**Important**: Keep your existing `OPENAI_API_KEY` line but make it optional:
```bash
OPENAI_API_KEY=your_existing_key  # Not needed when using Gemini
```

## Step 3: Install Dependencies

```bash
cd ~/personal-ai-job-assistant/src/backend
poetry add google-generativeai
```

## Step 4: Restart Server

```bash
# Stop current server (Ctrl+C)
# Then restart:
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Step 5: Test It!

```bash
cd ~/personal-ai-job-assistant/scripts
./test_ai_tailor.sh
```

You should see:
```
✅ Resume version created successfully!
Using Google Gemini as AI provider
```

---

## 🔄 Switching Between Providers

### Use Gemini (FREE):
```bash
AI_PROVIDER=gemini
GEMINI_API_KEY=AIza...
```

### Use OpenAI (Paid):
```bash
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

---

## 📊 Model Comparison

| Feature | Gemini Pro (FREE) | GPT-3.5-Turbo | GPT-4 |
|---------|-------------------|---------------|-------|
| **Cost** | $0 | ~$0.005/request | ~$0.15/request |
| **Speed** | Fast | Very Fast | Moderate |
| **Quality** | Good | Good | Excellent |
| **Rate Limit** | 60 RPM | Pay-per-use | Pay-per-use |

---

## 🐛 Troubleshooting

### Error: "Invalid API key"
- Check you copied the full key (starts with `AIza`)
- No quotes needed in .env file
- Restart uvicorn after changing .env

### Error: "Module 'google.generativeai' not found"
```bash
poetry add google-generativeai
```

### Error: "Rate limit exceeded"
- Free tier allows 60 requests/minute
- Wait 1 minute and retry
- For higher limits, upgrade to paid tier

---

## 🎉 Success!

Once working, you have:
- ✅ Free AI resume tailoring
- ✅ Unlimited testing (60 requests/min)
- ✅ No credit card required
- ✅ Easy switch to OpenAI later

Enjoy your FREE AI-powered job assistant! 🚀
