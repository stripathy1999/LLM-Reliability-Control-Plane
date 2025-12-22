# 🎭 Failure Theater Demo Guide

## The "Wow" Moment

This is your secret weapon. When judges see you click a button and watch production break in real-time, they remember you.

## Demo Flow (2 minutes)

### Setup (30 seconds)
1. Open Failure Theater: `http://localhost:3000`
2. Show the beautiful UI: "This is our Live Failure Theater"
3. Point out the health score: "Currently healthy at 85"

### The Magic (90 seconds)

**Step 1: Trigger Cost Explosion (30s)**
- Click the red "Cost Explosion" button
- Watch the health score drop to 45 (critical)
- Show the recommendation: "AI suggests downgrading model to save 30%"
- Say: "In Datadog, you'll see the cost anomaly monitor trigger and an incident get created automatically"

**Step 2: Trigger Latency Spike (30s)**
- Click the orange "Latency Spike" button
- Watch health score drop to 55 (degraded)
- Show the recommendation: "Suggests checking APM traces"
- Say: "The latency SLO monitor just triggered. Check Datadog - you'll see the incident with full context attached"

**Step 3: Show the Impact (30s)**
- Point to incident count: "We've created 2 incidents automatically"
- Show the status panel: "Each incident has dashboard, logs, traces, and AI recommendations attached"
- Say: "This is observability that drives action, not just awareness"

## What Judges See

1. **Visual Impact**: Beautiful, modern UI (not a terminal script)
2. **Real-Time**: Health scores update instantly
3. **Automation**: Incidents created automatically
4. **Intelligence**: AI recommendations appear immediately
5. **Professionalism**: You care about UX, not just backend

## Key Talking Points

- "One click breaks production - watch what happens"
- "Health score drops from 85 to 45 in seconds"
- "Datadog automatically creates an incident with full context"
- "AI recommendations tell engineers exactly what to do"
- "This is observability that drives action"

## Pro Tips

1. **Practice the clicks**: Make it smooth, not rushed
2. **Point to Datadog**: Have Datadog dashboard open in another tab
3. **Show the recommendations**: Read them out loud
4. **Emphasize automation**: "No manual investigation needed"
5. **End with impact**: "This is how observability should work"

## Troubleshooting

**Health score not updating?**
- Make sure FastAPI backend is running
- Check browser console for errors
- Verify API URL in `.env.local`

**Buttons not working?**
- Check network tab for API calls
- Verify backend endpoints are accessible
- Check CORS settings if deployed separately

**Want to reset?**
- Click "Reset System" button
- Or refresh the page

## Why This Wins

- **Memorable**: Judges remember the visual demo
- **Professional**: Shows you care about UX
- **Complete**: Demonstrates end-to-end flow
- **Impressive**: One-click failure scenarios
- **Different**: Most teams show scripts, you show a beautiful UI

---

**Remember**: This is your "flash upgrade" - the moment judges go "wow, this is different." Use it well!

