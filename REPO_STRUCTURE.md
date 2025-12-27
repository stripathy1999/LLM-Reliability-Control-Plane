# 📁 Repository Structure

Complete guide to the repository structure for hackathon submission.

## 📦 Required Files for Submission

### ✅ Core Application Files

```
LLM-Reliability-Control-Plane/
├── README.md                          ✅ REQUIRED - Main documentation
├── LICENSE                            ✅ REQUIRED - MIT License (OSI approved)
├── requirements.txt                   ✅ REQUIRED - Python dependencies
├── .gitignore                         ✅ RECOMMENDED - Exclude unnecessary files
│
├── app/                               ✅ REQUIRED - FastAPI application
│   ├── main.py                       ✅ Application entry point
│   ├── config.py                     ✅ Configuration settings
│   ├── llm_client.py                ✅ Gemini/Vertex AI client
│   ├── telemetry.py                  ✅ Datadog metrics & logs
│   ├── health_score.py               ✅ Composite health score calculation
│   ├── insights.py                   ✅ AI-powered insights
│   ├── quality_signals.py            ✅ Quality metrics computation
│   ├── routes/                       ✅ API endpoints
│   │   ├── qa.py                     ✅ Q&A endpoint
│   │   ├── reason.py                 ✅ Reasoning endpoint
│   │   ├── stress.py                 ✅ Stress testing endpoint
│   │   └── insights.py               ✅ Insights endpoint
│   └── static/                       ✅ Swagger UI customizations
│       ├── swagger-ui-custom.css     ✅ Enhanced styling
│       └── swagger-ui-custom.js      ✅ Interactive features
│
├── datadog/                          ✅ REQUIRED - Datadog configurations
│   ├── monitors.json                 ✅ REQUIRED - 5 detection rules
│   ├── dashboard.json                ✅ REQUIRED - Comprehensive dashboard
│   └── slo.json                      ✅ REQUIRED - Latency SLO
│
├── traffic-generator/                 ✅ REQUIRED - Load testing
│   └── generate_load.py             ✅ Traffic generation script
│
├── failure-theater/                   ✅ OPTIONAL - Bonus UI
│   ├── app/                          ✅ Next.js application
│   ├── package.json                  ✅ Node dependencies
│   └── README.md                     ✅ Frontend documentation
│
└── scripts/                          ✅ OPTIONAL - Helper scripts
    └── import_datadog_resources.py   ✅ Datadog import helper
```

## 📚 Documentation Files

### Required Documentation
- ✅ **README.md** - Main documentation with setup and testing
- ✅ **LICENSE** - MIT License

### Recommended Documentation
- ✅ **TESTING_GUIDE.md** - Complete testing instructions
- ✅ **DATADOG_SETUP.md** - Datadog configuration guide
- ✅ **REQUIREMENTS_COMPLIANCE.md** - Requirements checklist
- ✅ **SUBMISSION_CHECKLIST.md** - Pre-submission checklist
- ✅ **SUBMISSION_GUIDE.md** - Submission instructions
- ✅ **TESTING_VERIFICATION.md** - Testing verification guide

### Optional Documentation
- **QUICK_START.md** - Quick start guide
- **INNOVATION_FEATURES.md** - Innovation features explained
- **INCIDENT_CREATION_GUIDE.md** - Incident setup guide
- **VIDEO_SCRIPT.md** - Video walkthrough script

## 🚫 Files to Exclude (via .gitignore)

### Python
- `__pycache__/` - Python cache
- `*.pyc`, `*.pyo` - Compiled Python files
- `venv/`, `env/` - Virtual environments
- `*.egg-info/` - Package metadata

### Node
- `node_modules/` - Node dependencies
- `.next/`, `out/` - Next.js build outputs
- `npm-debug.log*` - Log files

### Environment
- `.env` - Environment variables (may contain secrets)
- `.env.local` - Local environment variables

### IDE
- `.vscode/`, `.idea/` - IDE settings
- `*.swp`, `*.swo` - Editor swap files

### OS
- `.DS_Store` - macOS system files
- `Thumbs.db` - Windows system files

### Build/Test
- `build/`, `dist/` - Build outputs
- `.pytest_cache/` - Test cache
- `*.log` - Log files

## ✅ Files to Keep

### Source Code
- All `.py` files in `app/`
- All `.tsx`, `.ts`, `.js` files in `failure-theater/app/`
- Configuration files (`package.json`, `requirements.txt`, etc.)

### Datadog Configurations
- `datadog/monitors.json` ✅ REQUIRED
- `datadog/dashboard.json` ✅ REQUIRED
- `datadog/slo.json` ✅ REQUIRED

### Documentation
- All `.md` files (README, guides, etc.)
- `LICENSE` file ✅ REQUIRED

### Scripts
- `traffic-generator/generate_load.py` ✅ REQUIRED
- Helper scripts in `scripts/`

## 📋 Pre-Push Checklist

Before pushing to GitHub:

- [ ] Remove sensitive data (API keys, credentials)
- [ ] Verify .gitignore excludes venv/, node_modules/, .env
- [ ] Ensure LICENSE file is present
- [ ] Verify README.md is complete
- [ ] Check all required files are present
- [ ] Remove any temporary files
- [ ] Remove any personal notes or TODOs
- [ ] Verify no large binary files
- [ ] Check file sizes (no huge files)

## 🔍 File Size Guidelines

- **Source files**: Should be reasonable (< 1MB each)
- **JSON configs**: Should be < 100KB each
- **Documentation**: No size limit, but keep focused
- **Exclude**: Large binary files, videos, screenshots (unless required)

## 📝 Required File Contents

### README.md Must Include:
- ✅ Project description
- ✅ Installation instructions
- ✅ Testing guide
- ✅ API documentation
- ✅ Datadog setup instructions
- ✅ Submission information (URLs, org name)

### LICENSE Must:
- ✅ Be OSI approved (MIT is good)
- ✅ Include copyright notice
- ✅ Include full license text

### requirements.txt Must:
- ✅ List all Python dependencies
- ✅ Include version pins if needed
- ✅ Be installable via `pip install -r requirements.txt`

## 🎯 Submission File Checklist

### Hard Requirements
- [x] **LICENSE** - MIT License ✅
- [x] **README.md** - Complete documentation ✅
- [x] **datadog/monitors.json** - 5 monitors ✅
- [x] **datadog/dashboard.json** - Dashboard ✅
- [x] **datadog/slo.json** - SLO definition ✅
- [x] **traffic-generator/generate_load.py** - Traffic generator ✅
- [x] **app/** - FastAPI application ✅
- [x] **requirements.txt** - Dependencies ✅

### Recommended Files
- [x] **.gitignore** - Exclude unnecessary files ✅
- [x] **TESTING_GUIDE.md** - Testing instructions ✅
- [x] **DATADOG_SETUP.md** - Datadog setup ✅
- [x] **SUBMISSION_GUIDE.md** - Submission instructions ✅

### Optional Files
- [x] **failure-theater/** - Bonus UI ✅
- [x] **scripts/** - Helper scripts ✅
- [x] **Additional documentation** - Various guides ✅

## 🚀 Quick Verification

Run these commands to verify repository structure:

```bash
# Check required files exist
ls README.md LICENSE requirements.txt
ls datadog/monitors.json datadog/dashboard.json datadog/slo.json
ls traffic-generator/generate_load.py
ls app/main.py

# Check .gitignore excludes sensitive files
cat .gitignore | grep -E "(venv|node_modules|\.env)"

# Verify LICENSE is MIT
head -1 LICENSE
```

## 📦 Final Repository Contents

Your repository should contain:

1. **Source Code** - Complete FastAPI application
2. **Datadog Configs** - All JSON exports
3. **Documentation** - Comprehensive guides
4. **Scripts** - Traffic generator and helpers
5. **License** - MIT License
6. **Configuration** - requirements.txt, package.json, etc.

**Exclude:**
- Virtual environments
- Node modules
- Environment files with secrets
- Build artifacts
- Cache files
- IDE settings

---

**Your repository is ready for submission!** 🎉


