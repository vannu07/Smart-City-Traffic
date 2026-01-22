"""
Smart City Traffic Management System - API Routes

This module defines all API endpoints for the traffic management system.
"""

from flask import Blueprint, jsonify, request, current_app
import time

# Create API blueprint
api_bp = Blueprint('api', __name__)

@api_bp.route('/')
def api_info():
    """API information and available endpoints"""
    return jsonify({
        "name": "Smart City Traffic Management API",
        "version": "1.0.0",
        "description": "ML-powered traffic management system with real-time analysis",
        "endpoints": {
            "GET /traffic": "Get current traffic data with ML classification",
            "GET /anomalies": "Get detected traffic anomalies",
            "GET /route": "Get optimized route (params: start, end)",
            "GET /stats": "Get comprehensive traffic statistics",
            "GET /config": "Get API configuration (debug mode only)"
        },
        "ml_models": {
            "clustering": "KMeans for traffic level classification",
            "anomaly_detection": "Isolation Forest for unusual pattern detection",
            "route_optimization": "NetworkX shortest path with congestion weights"
        },
        "data_sources": {
            "simulation": "Built-in traffic simulation",
            "external_apis": "Optional integration with Google Maps, etc."
        }
    })

@api_bp.route('/traffic', methods=['GET'])
def get_traffic_data():
    """
    Get current traffic data with ML-based congestion classification
    
    Returns:
        JSON response with traffic data for all road segments including:
        - Vehicle counts
        - Congestion scores (0-100)
        - ML-classified congestion levels (Low/Medium/High)
        - GPS coordinates
        - Timestamps
    """
    try:
        traffic_data = current_app.ml_system.get_current_traffic()
        
        return jsonify({
            "status": "success",
            "data": traffic_data,
            "metadata": {
                "total_roads": len(traffic_data),
                "timestamp": time.time(),
                "ml_classification": "KMeans clustering applied",
                "update_interval": current_app.config.get('AUTO_REFRESH_INTERVAL', 5)
            }
        })
        
    except Exception as e:
        current_app.logger.exception("Failed to retrieve traffic data")
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve traffic data due to an internal error",
            "timestamp": time.time()
        }), 500

@api_bp.route('/anomalies', methods=['GET'])
def get_anomalies():
    """
    Get detected traffic anomalies using ML anomaly detection
    
    Returns:
        JSON response with detected anomalies including:
        - Anomaly scores
        - Severity levels
        - Location details
        - Detection timestamps
    """
    try:
        anomalies = current_app.ml_system.detect_anomalies()
        
        return jsonify({
            "status": "success",
            "anomalies": anomalies,
            "metadata": {
                "total_anomalies": len(anomalies),
                "timestamp": time.time(),
                "detection_method": "Isolation Forest",
                "severity_levels": ["Low", "Medium", "High"]
            }
        })
        
    except Exception as e:
        current_app.logger.exception("Failed to detect anomalies")
        return jsonify({
            "status": "error",
            "message": "Failed to detect anomalies due to an internal error",
            "timestamp": time.time()
        }), 500

@api_bp.route('/route', methods=['GET'])
def get_optimized_route():
    """
    Get optimized route between two points considering real-time traffic
    
    Query Parameters:
        start (str): Starting location identifier
        end (str): Ending location identifier
    
    Returns:
        JSON response with optimized route including:
        - Path coordinates
        - Total distance
        - Estimated travel time
        - Route segments with congestion info
    """
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        
        if not start or not end:
            return jsonify({
                "status": "error",
                "message": "Both 'start' and 'end' parameters are required",
                "example": "/api/route?start=A&end=B",
                "available_locations": current_app.ml_system.get_available_locations()
            }), 400
        
        route = current_app.ml_system.get_optimized_route(start, end)
        
        return jsonify({
            "status": "success",
            "route": route,
            "metadata": {
                "timestamp": time.time(),
                "optimization_method": "NetworkX shortest path with congestion weights",
                "start_location": start,
                "end_location": end
            }
        })
        
    except Exception as e:
        current_app.logger.exception("Failed to calculate route")
        return jsonify({
            "status": "error",
            "message": "Failed to calculate route due to an internal error",
            "timestamp": time.time()
        }), 500

@api_bp.route('/stats', methods=['GET'])
def get_traffic_stats():
    """
    Get comprehensive traffic statistics and analytics
    
    Returns:
        JSON response with:
        - Current traffic metrics
        - Congestion distribution
        - Historical trends
        - Road type statistics
        - Anomaly counts
    """
    try:
        stats = current_app.ml_system.get_traffic_stats()
        
        return jsonify({
            "status": "success",
            "stats": stats,
            "metadata": {
                "timestamp": time.time(),
                "analytics_period": "Real-time + Historical",
                "ml_insights": "Clustering and anomaly detection applied"
            }
        })
        
    except Exception as e:
        current_app.logger.exception("Failed to retrieve statistics")
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve statistics due to an internal error",
            "timestamp": time.time()
        }), 500

@api_bp.route('/locations', methods=['GET'])
def get_available_locations():
    """
    Get list of available locations for route planning
    
    Returns:
        JSON response with available start/end points for routing
    """
    try:
        locations = current_app.ml_system.get_available_locations()
        
        return jsonify({
            "status": "success",
            "locations": locations,
            "metadata": {
                "total_locations": len(locations),
                "timestamp": time.time(),
                "usage": "Use these identifiers in /route endpoint"
            }
        })
        
    except Exception as e:
        current_app.logger.exception("Failed to retrieve locations")
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve locations due to an internal error",
            "timestamp": time.time()
        }), 500

@api_bp.route('/ml-status', methods=['GET'])
def get_ml_status():
    """
    Get status of ML models and their performance metrics
    
    Returns:
        JSON response with ML model status and metrics
    """
    try:
        ml_status = current_app.ml_system.get_ml_status()
        
        return jsonify({
            "status": "success",
            "ml_status": ml_status,
            "metadata": {
                "timestamp": time.time(),
                "models_active": True
            }
        })
        
    except Exception as e:
        current_app.logger.exception("Failed to retrieve ML status")
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve ML status due to an internal error",
            "timestamp": time.time()
        }), 500

# === UTILITY ENDPOINTS ===

@api_bp.route('/reset', methods=['POST'])
def reset_simulation():
    """
    Reset traffic simulation (development/testing only)
    
    Returns:
        JSON response confirming reset
    """
    if not current_app.config.get('DEBUG', False):
        return jsonify({
            "status": "error",
            "message": "Reset endpoint only available in debug mode"
        }), 403
    
    try:
        current_app.ml_system.reset_simulation()
        
        return jsonify({
            "status": "success",
            "message": "Traffic simulation reset successfully",
            "timestamp": time.time()
        })
        
    except Exception as e:
        current_app.logger.exception("Failed to reset simulation")
        return jsonify({
            "status": "error",
            "message": "Failed to reset simulation due to an internal error",
            "timestamp": time.time()
        }), 500