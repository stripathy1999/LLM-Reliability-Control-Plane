# ✅ Ready to Deploy - Your Complete Checklist

## 🎯 What You Have

✅ **Google Cloud Project ID**: `llm-reliability-control`

## 🔑 What You Need (4 Items)

1. **Gemini API Key** - https://aistudio.google.com/app/apikey
2. **Datadog API Key** - https://app.datadoghq.com/organization-settings/api-keys
3. **Datadog App Key** - https://app.datadoghq.com/organization-settings/application-keys
4. **Datadog Site** - Check your Datadog login URL (datadoghq.com, datadoghq.eu, etc.)

---

## 🚀 Quick Start (3 Commands)

### **Step 1: Setup Secrets**

**Windows PowerShell:**
```powershell
.\scripts\setup_gcp_secrets.ps1
# Enter: Gemini API Key, Datadog API Key, Datadog App Key, Datadog Site
```

**Linux/macOS:**
```bash
chmod +x scripts/setup_gcp_secrets.sh
./scripts/setup_gcp_secrets.sh
# Enter: Gemini API Key, Datadog API Key, Datadog App Key, Datadog Site
```

### **Step 2: Deploy**

**Windows PowerShell:**
```powershell
.\scripts\deploy_to_cloud_run.ps1
```

**Linux/macOS:**
```bash
chmod +x scripts/deploy_to_cloud_run.sh
./scripts/deploy_to_cloud_run.sh
```

### **Step 3: Get Service URL**

```bash
gcloud run services describe llm-reliability-control-plane --region us-central1 --format 'value(status.url)'
```

---

## 📋 Complete Deployment Checklist

### Before You Start
- [ ] Google Cloud SDK installed (`gcloud --version`)
- [ ] Authenticated with Google Cloud (`gcloud auth login`)
- [ ] Project set (`gcloud config set project llm-reliability-control`)
- [ ] Gemini API key obtained
- [ ] Datadog API key obtained
- [ ] Datadog App key obtained
- [ ] Datadog site identified

### Run Scripts
- [ ] Run `setup_gcp_secrets.ps1` (Windows) or `setup_gcp_secrets.sh` (Linux/macOS)
- [ ] Run `deploy_to_cloud_run.ps1` (Windows) or `deploy_to_cloud_run.sh` (Linux/macOS)
- [ ] Get service URL

### After Deployment
- [ ] Update `datadog/workflows.json` - Replace `{{APP_URL}}` with service URL
- [ ] Update `datadog/oncall.json` - Replace emails/channels
- [ ] Import Datadog resources (see `DATADOG_IMPORT_GUIDE.md`)
- [ ] Test application endpoints
- [ ] Verify Datadog integration

---

## 🎯 Expected Results

After deployment:
- ✅ Service URL: `https://llm-reliability-control-plane-xxxxx-uc.a.run.app`
- ✅ All endpoints working
- ✅ Datadog receiving traces, metrics, logs
- ✅ 19 Datadog products integrated

---

## 📚 Documentation

- **Complete Setup**: `COMPLETE_SETUP_GUIDE.md`
- **Quick Deploy**: `QUICK_DEPLOY.md`
- **Your Steps**: `YOUR_DEPLOYMENT_STEPS.md`
- **Datadog Import**: `DATADOG_IMPORT_GUIDE.md`
- **Deployment Guide**: `DEPLOYMENT_GUIDE.md`

---

**🚀 You're Ready!** Get the 4 API keys and run the scripts!

