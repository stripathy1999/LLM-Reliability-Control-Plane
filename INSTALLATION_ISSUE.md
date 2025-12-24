# Installation Issue: grpcio on Windows/MSYS

## Problem

The `grpcio` package cannot be built from source on Windows when using MSYS/MinGW Python environments. This is a known limitation due to compilation issues with native extensions.

## Error

```
distutils.compilers.C.errors.UnknownFileType: unknown file type '.s' (from 'third_party\boringssl-with-bazel\src\crypto\curve25519\asm\x25519-asm-arm.s')
```

## Solutions

### Option 1: Use Standard Windows Python (Recommended)

1. Install Python from [python.org](https://www.python.org/downloads/) (not MSYS)
2. Create a new virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

### Option 2: Use WSL (Windows Subsystem for Linux)

1. Install WSL2
2. Use Linux Python environment where grpcio builds successfully

### Option 3: Use Pre-built Wheel (if available)

Try installing from a pre-built wheel:
```powershell
pip install grpcio --only-binary :all:
```

Note: This may not work if no wheel is available for your specific platform.

## Current Status

- ✅ Most dependencies installed successfully
- ✅ google-generativeai package installed
- ❌ grpcio cannot be built (blocks google-generativeai from working)
- ❌ Server cannot start without grpcio

## Next Steps

Once grpcio is installed, you can:
1. Set your Gemini API key: `$env:GEMINI_API_KEY = "your-key-here"`
2. Start the server: `uvicorn app.main:app --reload`
3. Run tests: `python test_end_to_end.py`

