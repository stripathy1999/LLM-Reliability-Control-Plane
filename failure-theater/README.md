# 🎭 Live Failure Theater

A visually stunning, one-click failure scenario trigger for the LLM Reliability Control Plane demo.

## What It Does

This Next.js application provides a beautiful, interactive UI that allows you to trigger production failure scenarios with a single click. Perfect for hackathon demos where you need to show incidents being created in real-time.

## Features

- **🔴 Cost Explosion**: Triggers cost anomaly monitor
- **🟠 Latency Spike**: Breaches SLO threshold
- **🔵 Quality Drop**: Degrades similarity score
- **⚫ Security Attack**: Triggers safety blocks

Each button:
- Sends multiple requests to your FastAPI backend
- Updates health score in real-time
- Shows incident creation status
- Displays AI-powered recommendations

## Setup

1. Install dependencies:
```bash
cd failure-theater
npm install
```

2. Set API URL (optional, defaults to `http://localhost:8000`):
```bash
# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

3. Start the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000)

## Usage

1. Make sure your FastAPI backend is running on port 8000
2. Open the Failure Theater in your browser
3. Click any failure button to trigger a scenario
4. Watch the health score update and incidents get created
5. Check Datadog dashboard to see monitors trigger

## Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Docker

```bash
docker build -t failure-theater .
docker run -p 3000:3000 failure-theater
```

## Customization

Edit `app/page.tsx` to:
- Change button colors/styles
- Modify health score calculation
- Add new failure scenarios
- Customize recommendations

## Why This Wins

- **Visual Impact**: Judges see incidents being created in real-time
- **One-Click Demo**: No scripts, no terminal, just click
- **Memorable**: Beautiful UI that stands out
- **Professional**: Shows you care about UX, not just backend





