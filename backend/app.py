from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import threading
import time
from traffic_ml import TrafficMLSystem

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize the ML system
traffic_system = TrafficMLSystem()

@app.route('/')
def home():
    return jsonify({
        "message": "Smart City Traffic Management API",
        "endpoints": {
            "/traffic": "Get current traffic data",
            "/anomalies": "Get traffic anomalies",
            "/route": "Get optimized route (params: start, end)",
            "/stats": "Get traffic statistics"
        }
    })

@app.route('/traffic', methods=['GET'])
def get_traffic_data():
    """Get current traffic data with congestion levels"""
    try:
        traffic_data = traffic_system.get_current_traffic()
        return jsonify({
            "status": "success",
            "data": traffic_data,
            "timestamp": time.time()
        })
    except Exception as e:
        app.logger.exception("Error while getting current traffic data")
        return jsonify({
            "status": "error",
            "message": "An internal error occurred. Please try again later."
        }), 500

@app.route('/anomalies', methods=['GET'])
def get_anomalies():
    """Get detected traffic anomalies"""
    try:
        anomalies = traffic_system.detect_anomalies()
        return jsonify({
            "status": "success",
            "anomalies": anomalies,
            "timestamp": time.time()
        })
    except Exception as e:
        app.logger.exception("Error while detecting traffic anomalies")
        return jsonify({
            "status": "error",
            "message": "An internal error occurred. Please try again later."
        }), 500

@app.route('/route', methods=['GET'])
def get_optimized_route():
    """Get optimized route between two points"""
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        
        if not start or not end:
            return jsonify({
                "status": "error",
                "message": "Both 'start' and 'end' parameters are required"
            }), 400
        
        route = traffic_system.get_optimized_route(start, end)
        return jsonify({
            "status": "success",
            "route": route,
            "timestamp": time.time()
        })
    except Exception as e:
        app.logger.exception("Error while getting optimized route")
        return jsonify({
            "status": "error",
            "message": "An internal error occurred. Please try again later."
        }), 500

@app.route('/stats', methods=['GET'])
def get_traffic_stats():
    """Get traffic statistics and metrics"""
    try:
        stats = traffic_system.get_traffic_stats()
        return jsonify({
            "status": "success",
            "stats": stats,
            "timestamp": time.time()
        })
    except Exception as e:
        app.logger.exception("Error while getting traffic statistics")
        return jsonify({
            "status": "error",
            "message": "An internal error occurred. Please try again later."
        }), 500

def update_traffic_data():
    """Background thread to continuously update traffic data"""
    while True:
        try:
            traffic_system.update_traffic_simulation()
            time.sleep(5)  # Update every 5 seconds
        except Exception as e:
            print(f"Error updating traffic data: {e}")
            time.sleep(10)

if __name__ == '__main__':
    # Start background traffic simulation
    traffic_thread = threading.Thread(target=update_traffic_data, daemon=True)
    traffic_thread.start()
    
    print("🚦 Smart City Traffic Management System Starting...")
    print("📊 ML Models: Clustering, Anomaly Detection, Route Optimization")
    print("🌐 API Server: http://localhost:5000")
    print("📡 Real-time traffic simulation active")
    
    app.run(host='0.0.0.0', port=5000, threaded=True)