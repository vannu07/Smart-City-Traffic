"""
Smart City Traffic Management System - Flask Application Factory

This module creates and configures the Flask application with all routes,
middleware, and background services.
"""

import threading
import time
from pathlib import Path

from flask import Flask, render_template, jsonify
from flask_cors import CORS

from .routes import api_bp
from ..ml.traffic_ml import TrafficMLSystem

def create_app(config):
    """Create and configure Flask application"""

    # Create Flask app
    app = Flask(__name__,
                template_folder=str(Path(__file__).parent.parent.parent / "templates"),
                static_folder=str(Path(__file__).parent.parent.parent / "static"))

    # Configure app
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['DEBUG'] = config.DEBUG

    # Enable CORS
    CORS(app, origins=config.CORS_ORIGINS)

    # Initialize ML system
    app.ml_system = TrafficMLSystem(config)

    # Register API blueprint
    app.register_blueprint(api_bp, url_prefix=config.API_PREFIX)

    # === MAIN ROUTES ===

    @app.route('/')
    def index():
        """Main landing page"""
        return jsonify({
            "message": "🚦 Smart City Traffic Management System",
            "version": "1.0.0",
            "status": "active",
            "endpoints": {
                "dashboard": "/dashboard",
                "api_docs": "/api",
                "health": "/health"
            },
            "ml_models": {
                "clustering": "KMeans (Traffic Classification)",
                "anomaly_detection": "Isolation Forest",
                "route_optimization": "NetworkX Shortest Path"
            }
        })

    @app.route('/dashboard')
    def dashboard():
        """Serve the main dashboard"""
        return render_template('dashboard.html',
                             config=config.get_frontend_config(),
                             api_config=config.get_api_config())

    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        validation = config.validate_config()
        return jsonify({
            "status": "healthy",
            "timestamp": time.time(),
            "config_status": validation['status'],
            "warnings": validation.get('warnings', []),
            "ml_system": "active",
            "api_endpoints": len(api_bp.deferred_functions),
            "environment": config.ENVIRONMENT
        })

    @app.route('/config')
    def get_config():
        """Get current configuration (for debugging)"""
        if not config.DEBUG:
            return jsonify({"error": "Config endpoint only available in debug mode"}), 403

        return jsonify({
            "api_config": config.get_api_config(),
            "ml_config": config.get_ml_config(),
            "frontend_config": config.get_frontend_config()
        })

    # === ERROR HANDLERS ===

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({
            "error": "Endpoint not found",
            "message": "The requested endpoint does not exist",
            "available_endpoints": [
                "/dashboard",
                "/api/traffic",
                "/api/anomalies",
                "/api/route",
                "/api/stats",
                "/health"
            ]
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }), 500

    # === BACKGROUND SERVICES ===

    def start_background_services():
        """Start background services for traffic simulation"""
        def update_traffic_data():
            """Background thread to continuously update traffic data"""
            while True:
                try:
                    app.ml_system.update_traffic_simulation()
                    time.sleep(config.AUTO_REFRESH_INTERVAL)
                except Exception:
                    print("Error updating traffic data")
                    time.sleep(config.AUTO_REFRESH_INTERVAL * 2)

        # Start background traffic simulation
        traffic_thread = threading.Thread(target=update_traffic_data, daemon=True)
        traffic_thread.start()

        print(f"✅ Background services started (refresh every {config.AUTO_REFRESH_INTERVAL}s)")

    # Start background services
    start_background_services()

    return app
