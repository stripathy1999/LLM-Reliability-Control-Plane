# 🎬 Video Script - 3-Minute Datadog Challenge Demo

**Target Length:** 3 minutes (180 seconds)  
**Format:** Screen recording with voiceover  
**Focus:** Answer the 3 critical questions + showcase innovation

---

## 📋 Pre-Recording Checklist

- [ ] Application deployed and accessible
- [ ] Datadog dashboard imported and populated
- [ ] All monitors imported and active
- [ ] Incident rules configured
- [ ] Traffic generator ready
- [ ] Swagger UI accessible
- [ ] Failure Theater UI accessible (optional)
- [ ] All screenshots prepared

---

## 🎯 Video Structure (180 seconds)

### **Opening (0:00 - 0:15)** - 15 seconds

**Visual:** Show application running, Datadog dashboard

**Script:**
> "Hi! I'm [Name], and this is the LLM Reliability Control Plane - a comprehensive observability solution for Large Language Model applications built for the Datadog hackathon challenge. This solution answers three critical questions: What failed? Why did it fail? And what should the engineer do next?"

**Key Points:**
- Introduce yourself
- Name the project
- State the 3 questions

---

### **Part 1: What Failed? (0:15 - 0:45)** - 30 seconds

**Visual:** Show Datadog dashboard with health score, monitors, metrics

**Script:**
> "First, what failed? Our composite health score gives you a single metric - zero to 100 - that combines performance, reliability, cost, quality, and security. Right now, we're at 85, which is healthy. But watch what happens when we trigger a failure scenario."

**Action:** 
- Click "Cost Explosion" button in Failure Theater (or trigger via API)
- Show health score dropping to 45
- Show monitor triggering (red alert)

**Script (continued):**
> "The health score dropped to 45, and our cost anomaly monitor triggered. The dashboard shows exactly what failed - cost per request spiked above our threshold."

**Key Points:**
- Show health score widget
- Show monitor alerting
- Show metrics on dashboard

---

### **Part 2: Why Did It Fail? (0:45 - 1:30)** - 45 seconds

**Visual:** Show incident with runbook, logs, traces

**Script:**
> "Now, why did it fail? When the monitor triggered, Datadog automatically created an incident with full context. The incident includes a complete runbook that explains possible causes - in this case, long context prompts consuming excessive tokens, or a potential token abuse attack."

**Action:**
- Open incident in Datadog
- Show runbook in incident description
- Show attached logs (filtered by service)
- Show attached traces (if available)

**Script (continued):**
> "We can see in the logs that requests had unusually high input token counts. The traces show the exact spans where token counting occurred. This trace-log-metric correlation gives us complete context."

**Key Points:**
- Show incident creation
- Show runbook
- Show log correlation
- Show trace correlation

---

### **Part 3: What Should the Engineer Do Next? (1:30 - 2:15)** - 45 seconds

**Visual:** Show insights endpoint, recommendations, ML predictions

**Script:**
> "Finally, what should the engineer do next? Our insights endpoint provides AI-powered recommendations. Let me call it."

**Action:**
- Open Swagger UI or terminal
- Call `/insights` endpoint
- Show response with recommendations

**Script (continued):**
> "The system recommends: downgrade to a cheaper model tier, implement response caching, or add prompt length limits. It even estimates potential savings - 30% cost reduction. We also have ML-based cost prediction that forecasts costs 24 hours ahead with 85% accuracy."

**Action:**
- Show recommendations in response
- Show predictive insights
- Show ML model status

**Key Points:**
- Show actionable recommendations
- Show cost savings estimates
- Show ML predictions

---

### **Part 4: Innovation Highlights (2:15 - 2:50)** - 35 seconds

**Visual:** Quick showcase of advanced features

**Script:**
> "What makes this solution stand out? First, we go beyond standard observability - we track cost, quality, and security, not just performance. Second, we use ML-based anomaly detection with Datadog Watchdog, not just thresholds. Third, we provide predictive insights that forecast issues before they happen."

**Action:**
- Show anomaly detection monitors
- Show quality metrics
- Show security signals
- Show predictive insights

**Script (continued):**
> "We also have custom spans for LLM-specific operations, full trace-log-metric correlation, and Datadog notebooks for root cause analysis. This is observability that drives action, not just awareness."

**Key Points:**
- Highlight innovation features
- Show advanced Datadog features
- Emphasize actionability

---

### **Closing (2:50 - 3:00)** - 10 seconds

**Visual:** Show dashboard again, all green/healthy

**Script:**
> "This solution provides end-to-end observability for LLM applications, answering all three critical questions with actionable insights. Thank you for watching!"

**Action:**
- Reset health score (if possible)
- Show healthy dashboard
- End screen with project name

**Key Points:**
- Summarize value
- Thank viewers

---

## 🎥 Recording Tips

### **Before Recording:**
1. Close unnecessary applications
2. Set screen resolution to 1920x1080
3. Test microphone audio
4. Prepare all browser tabs (Datadog, Swagger, Failure Theater)
5. Have traffic generator ready
6. Practice the script 2-3 times

### **During Recording:**
1. Speak clearly and at moderate pace
2. Pause briefly when showing UI elements
3. Use cursor to highlight important areas
4. Don't rush - 3 minutes is enough time
5. If you make a mistake, pause and re-record that section

### **After Recording:**
1. Edit out long pauses
2. Add text overlays for key points (optional)
3. Add background music (optional, keep it subtle)
4. Export in 1080p quality
5. Upload to YouTube/Vimeo

---

## 📝 Key Phrases to Use

- "Comprehensive observability"
- "Actionable insights"
- "ML-powered"
- "End-to-end correlation"
- "Beyond standard observability"
- "Drives action, not just awareness"
- "Three critical questions"
- "Composite health score"
- "Predictive insights"

---

## 🎯 What Judges Should See

1. ✅ **Clear demonstration** of the 3 questions being answered
2. ✅ **Automated incident creation** with full context
3. ✅ **Innovation features** (ML, cost observability, quality metrics)
4. ✅ **Advanced Datadog features** (custom spans, correlation, notebooks)
5. ✅ **Production-ready** solution (not just a demo)

---

## 📊 Timing Breakdown

| Section | Time | Key Action |
|---------|------|------------|
| Opening | 0:00-0:15 | Introduce project |
| What Failed? | 0:15-0:45 | Show health score + monitor trigger |
| Why Failed? | 0:45-1:30 | Show incident + runbook + correlation |
| What Next? | 1:30-2:15 | Show insights + recommendations |
| Innovation | 2:15-2:50 | Show advanced features |
| Closing | 2:50-3:00 | Summarize value |

**Total: 3:00 minutes**

---

## 🚀 Alternative Shorter Version (2 minutes)

If you need a shorter version:

1. **Opening (0:00-0:10)** - 10s
2. **What Failed? (0:10-0:35)** - 25s
3. **Why Failed? (0:35-1:05)** - 30s
4. **What Next? (1:05-1:40)** - 35s
5. **Innovation (1:40-1:55)** - 15s
6. **Closing (1:55-2:00)** - 5s

---

## ✅ Post-Recording Checklist

- [ ] Video uploaded to YouTube/Vimeo
- [ ] Video is public or unlisted
- [ ] Video link added to submission form
- [ ] Video description includes project name and key features
- [ ] Video thumbnail is clear and professional

---

**Good luck with your submission!** 🎉
