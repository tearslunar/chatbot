#!/usr/bin/env python3
"""
Simple test server to diagnose CORS and connectivity issues
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set working directory
os.chdir(Path(__file__).parent)

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 Starting Simple Test Server...")
    print("📁 Working directory:", os.getcwd())
    print("🐍 Python path:", sys.path[:3])
    
    try:
        print("✅ Starting server on http://0.0.0.0:8888")
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8888, 
            log_level="info",
            reload=False
        )
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        import traceback
        traceback.print_exc() 