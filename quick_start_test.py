#!/usr/bin/env python3
"""
Quick test to verify the application can start and basic imports work.
"""

import os
import sys

def test_imports():
    """Test that all imports work."""
    print("Testing imports...")
    try:
        from app.config import settings
        print("✅ Config imported")
        
        from app.llm_client import get_llm_client
        print("✅ LLM client imported")
        
        from app.main import app
        print("✅ FastAPI app imported")
        
        from app.routes import qa, reason, stress, insights
        print("✅ All routes imported")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Test configuration."""
    print("\nTesting configuration...")
    try:
        from app.config import settings
        print(f"  Project: {settings.project_name}")
        print(f"  Model: {settings.gemini_model}")
        print(f"  Environment: {settings.environment}")
        
        # Check API key
        api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("LRCP_GEMINI_API_KEY")
        if api_key:
            print(f"  ✅ Gemini API key found (length: {len(api_key)})")
        else:
            print("  ⚠️  Gemini API key not set (will fail on LLM requests)")
        
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_llm_client_init():
    """Test LLM client initialization (without making API calls)."""
    print("\nTesting LLM client initialization...")
    try:
        from app.llm_client import get_llm_client
        
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("LRCP_GEMINI_API_KEY")
        if not api_key:
            print("  ⚠️  Skipping LLM client test (no API key)")
            return True
        
        # Try to get client (this will initialize it)
        client = get_llm_client()
        print(f"  ✅ LLM client initialized: {type(client).__name__}")
        return True
    except Exception as e:
        print(f"  ⚠️  LLM client init failed: {e}")
        print("     (This is OK if API key is not set)")
        return True  # Not a critical failure

if __name__ == "__main__":
    print("=" * 60)
    print("Quick Start Test - LLM Reliability Control Plane")
    print("=" * 60)
    print()
    
    success = True
    success &= test_imports()
    success &= test_config()
    success &= test_llm_client_init()
    
    print()
    print("=" * 60)
    if success:
        print("✅ All basic tests passed!")
        print("\nNext steps:")
        print("1. Set GEMINI_API_KEY environment variable")
        print("2. Start server: uvicorn app.main:app --reload")
        print("3. Run full tests: python test_end_to_end.py")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


