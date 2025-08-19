#!/usr/bin/env python3
"""
Smart City Traffic Management System
Main Entry Point

This is the main application entry point that initializes and runs the
Smart City Traffic Management System with ML-powered traffic analysis.
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.api.app import create_app
from config.settings import Config

def main():
    """Main application entry point"""
    print("🚦 Smart City Traffic Management System")
    print("=" * 50)
    
    # Load configuration
    config = Config()
    
    print(f"📊 Environment: {config.ENVIRONMENT}")
    print(f"🌐 Server Host: {config.HOST}")
    print(f"🔌 Server Port: {config.PORT}")
    print(f"🔄 Debug Mode: {config.DEBUG}")
    print(f"📡 Auto-refresh: {config.AUTO_REFRESH_INTERVAL}s")
    
    # Create Flask application
    app = create_app(config)
    
    print("\n🚀 Starting server...")
    print(f"📍 API Base URL: http://{config.HOST}:{config.PORT}")
    print(f"🌍 Frontend URL: http://{config.HOST}:{config.PORT}/dashboard")
    print("\n📋 Available API Endpoints:")
    print(f"   • GET  /api/traffic     - Get current traffic data")
    print(f"   • GET  /api/anomalies   - Get traffic anomalies")
    print(f"   • GET  /api/route       - Get optimized route")
    print(f"   • GET  /api/stats       - Get traffic statistics")
    print(f"   • GET  /dashboard       - Web dashboard")
    print(f"   • GET  /health          - Health check")
    
    print("\n⚡ ML Models Active:")
    print("   • KMeans Clustering (Traffic Classification)")
    print("   • Isolation Forest (Anomaly Detection)")
    print("   • NetworkX (Route Optimization)")
    
    print("\n" + "=" * 50)
    print("🎯 Ready! Open your browser and navigate to the dashboard")
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 50 + "\n")
    
    try:
        # Run the application
        app.run(
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()