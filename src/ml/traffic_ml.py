"""
Smart City Traffic Management System - Machine Learning Module

This module contains all ML models and traffic simulation logic:
- Traffic data simulation with realistic patterns
- KMeans clustering for congestion classification
- Isolation Forest for anomaly detection
- NetworkX for route optimization
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import networkx as nx
import random
import time
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any, Optional

class TrafficMLSystem:
    """Main ML system for traffic management and analysis"""
    
    def __init__(self, config):
        """Initialize the ML system with configuration"""
        self.config = config
        self.ml_config = config.get_ml_config()
        
        # Initialize components
        self.road_segments = self._initialize_road_network()
        self.traffic_history = []
        self.current_traffic = {}
        self.graph = self._create_road_graph()
        
        # Initialize ML models
        self._initialize_ml_models()
        
        # Generate initial data for training
        self._generate_initial_data()
        
        print("✅ ML System initialized with:")
        print(f"   • {len(self.road_segments)} road segments")
        print(f"   • {self.graph.number_of_nodes()} intersections")
        print(f"   • {self.graph.number_of_edges()} road connections")
        print(f"   • Clustering: {self.ml_config['clustering']['algorithm']}")
        print(f"   • Anomaly Detection: {self.ml_config['anomaly_detection']['algorithm']}")
        
    def _initialize_ml_models(self):
        """Initialize ML models based on configuration"""
        # Clustering model
        clustering_config = self.ml_config['clustering']
        if clustering_config['algorithm'] == 'kmeans':
            self.clustering_model = KMeans(
                n_clusters=clustering_config['n_clusters'],
                random_state=clustering_config['random_state'],
                n_init=10
            )
        elif clustering_config['algorithm'] == 'dbscan':
            self.clustering_model = DBSCAN(eps=0.5, min_samples=5)
        
        # Anomaly detection model
        anomaly_config = self.ml_config['anomaly_detection']
        self.anomaly_detector = IsolationForest(
            contamination=anomaly_config['contamination'],
            random_state=anomaly_config['random_state']
        )
        
        # Scaler for feature normalization
        self.scaler = StandardScaler()
        
    def _initialize_road_network(self):
        """Initialize simulated road network for a smart city"""
        # Get map center from config
        center_lat = self.config.FRONTEND_CONFIG['map_center']['lat']
        center_lng = self.config.FRONTEND_CONFIG['map_center']['lng']
        
        # Create road network around the center point
        roads = [
            # Main arterial roads (North-South)
            {"id": "R001", "name": "Main Street", "start": [center_lat, center_lng], "end": [center_lat + 0.001, center_lng + 0.001], "type": "arterial"},
            {"id": "R002", "name": "Broadway", "start": [center_lat + 0.001, center_lng + 0.001], "end": [center_lat + 0.002, center_lng + 0.002], "type": "arterial"},
            {"id": "R003", "name": "Park Avenue", "start": [center_lat + 0.002, center_lng + 0.002], "end": [center_lat + 0.003, center_lng + 0.003], "type": "arterial"},
            {"id": "R004", "name": "5th Avenue", "start": [center_lat + 0.003, center_lng + 0.003], "end": [center_lat + 0.004, center_lng + 0.004], "type": "arterial"},
            {"id": "R005", "name": "Madison Ave", "start": [center_lat + 0.004, center_lng + 0.004], "end": [center_lat + 0.005, center_lng + 0.005], "type": "arterial"},
            
            # Cross streets (East-West)
            {"id": "R006", "name": "42nd Street", "start": [center_lat, center_lng], "end": [center_lat, center_lng + 0.006], "type": "collector"},
            {"id": "R007", "name": "34th Street", "start": [center_lat + 0.001, center_lng + 0.001], "end": [center_lat + 0.001, center_lng + 0.005], "type": "collector"},
            {"id": "R008", "name": "23rd Street", "start": [center_lat + 0.002, center_lng + 0.002], "end": [center_lat + 0.002, center_lng + 0.006], "type": "collector"},
            {"id": "R009", "name": "14th Street", "start": [center_lat + 0.003, center_lng + 0.003], "end": [center_lat + 0.003, center_lng + 0.005], "type": "collector"},
            {"id": "R010", "name": "Houston St", "start": [center_lat + 0.004, center_lng + 0.004], "end": [center_lat + 0.004, center_lng + 0.006], "type": "collector"},
            
            # Local roads
            {"id": "R011", "name": "1st Avenue", "start": [center_lat, center_lng + 0.006], "end": [center_lat + 0.005, center_lng + 0.006], "type": "local"},
            {"id": "R012", "name": "2nd Avenue", "start": [center_lat, center_lng + 0.005], "end": [center_lat + 0.005, center_lng + 0.005], "type": "local"},
            {"id": "R013", "name": "3rd Avenue", "start": [center_lat, center_lng + 0.004], "end": [center_lat + 0.005, center_lng + 0.004], "type": "local"},
            {"id": "R014", "name": "Lexington Ave", "start": [center_lat, center_lng + 0.003], "end": [center_lat + 0.005, center_lng + 0.003], "type": "local"},
            {"id": "R015", "name": "Park Ave South", "start": [center_lat, center_lng + 0.002], "end": [center_lat + 0.005, center_lng + 0.002], "type": "local"},
        ]
        return roads
    
    def _create_road_graph(self):
        """Create NetworkX graph for route optimization"""
        G = nx.Graph()
        
        # Add nodes (intersections)
        intersections = set()
        for road in self.road_segments:
            start_node = f"{road['start'][0]:.4f},{road['start'][1]:.4f}"
            end_node = f"{road['end'][0]:.4f},{road['end'][1]:.4f}"
            intersections.add(start_node)
            intersections.add(end_node)
        
        for intersection in intersections:
            lat, lon = map(float, intersection.split(','))
            G.add_node(intersection, pos=(lat, lon))
        
        # Add edges (roads)
        for road in self.road_segments:
            start_node = f"{road['start'][0]:.4f},{road['start'][1]:.4f}"
            end_node = f"{road['end'][0]:.4f},{road['end'][1]:.4f}"
            
            # Calculate distance (simplified)
            distance = np.sqrt(
                (road['end'][0] - road['start'][0])**2 + 
                (road['end'][1] - road['start'][1])**2
            ) * 111000  # Convert to meters approximately
            
            G.add_edge(start_node, end_node, 
                      road_id=road['id'], 
                      distance=distance, 
                      road_name=road['name'],
                      road_type=road['type'])
        
        return G
    
    def _generate_initial_data(self):
        """Generate initial traffic data for ML model training"""
        print("🔄 Generating initial training data...")
        
        for i in range(100):  # Generate 100 historical data points
            traffic_data = self._simulate_traffic_snapshot()
            self.traffic_history.append(traffic_data)
            
            if i % 20 == 0:
                print(f"   Generated {i}/100 training samples...")
        
        # Train initial models
        self._train_models()
        print("✅ Initial training completed")
    
    def _simulate_traffic_snapshot(self):
        """Simulate a single traffic data snapshot with realistic patterns"""
        current_time = datetime.now()
        hour = current_time.hour
        day_of_week = current_time.weekday()  # 0=Monday, 6=Sunday
        
        # Time-based traffic patterns
        rush_hour_multiplier = 1.0
        
        # Rush hour patterns
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # Morning and evening rush
            rush_hour_multiplier = 2.5
        elif 22 <= hour or hour <= 6:  # Night time
            rush_hour_multiplier = 0.3
        elif 10 <= hour <= 16:  # Midday
            rush_hour_multiplier = 1.2
        
        # Weekend patterns
        if day_of_week >= 5:  # Weekend
            rush_hour_multiplier *= 0.7
        
        # Apply simulation speed from config
        rush_hour_multiplier *= self.config.SIMULATION_SPEED
        
        traffic_snapshot = []
        
        for road in self.road_segments:
            # Base traffic based on road type
            base_traffic = {
                'arterial': random.randint(50, 150),
                'collector': random.randint(20, 80),
                'local': random.randint(5, 40)
            }
            
            vehicle_count = int(base_traffic[road['type']] * rush_hour_multiplier * random.uniform(0.7, 1.3))
            
            # Calculate congestion score (0-100)
            max_capacity = {
                'arterial': 200,
                'collector': 100,
                'local': 50
            }
            
            congestion_score = min(100, (vehicle_count / max_capacity[road['type']]) * 100)
            
            # Add some random variation and occasional spikes
            if random.random() < 0.05:  # 5% chance of traffic spike
                congestion_score = min(100, congestion_score * random.uniform(1.5, 2.0))
                vehicle_count = int(vehicle_count * random.uniform(1.5, 2.0))
            
            traffic_data = {
                'road_id': road['id'],
                'road_name': road['name'],
                'vehicle_count': vehicle_count,
                'congestion_score': round(congestion_score, 2),
                'timestamp': current_time.isoformat(),
                'coordinates': {
                    'start': road['start'],
                    'end': road['end']
                },
                'road_type': road['type']
            }
            
            traffic_snapshot.append(traffic_data)
        
        return traffic_snapshot
    
    def _train_models(self):
        """Train ML models with current data"""
        if len(self.traffic_history) < 10:
            return
        
        # Prepare features for training
        features = []
        for snapshot in self.traffic_history[-50:]:  # Use last 50 snapshots
            for road_data in snapshot:
                features.append([
                    road_data['vehicle_count'],
                    road_data['congestion_score'],
                    hash(road_data['road_type']) % 100  # Encode road type
                ])
        
        if features:
            features_array = np.array(features)
            
            # Train scaler and anomaly detector
            features_scaled = self.scaler.fit_transform(features_array)
            self.anomaly_detector.fit(features_scaled)
    
    def update_traffic_simulation(self):
        """Update traffic simulation (called by background thread)"""
        new_snapshot = self._simulate_traffic_snapshot()
        self.traffic_history.append(new_snapshot)
        
        # Keep only configured number of records
        max_records = self.config.MAX_HISTORY_RECORDS
        if len(self.traffic_history) > max_records:
            self.traffic_history = self.traffic_history[-max_records:]
        
        # Update current traffic data
        self.current_traffic = {road['road_id']: road for road in new_snapshot}
        
        # Retrain models periodically
        if len(self.traffic_history) % 20 == 0:
            self._train_models()
    
    def get_current_traffic(self) -> List[Dict[str, Any]]:
        """Get current traffic data with ML clustering"""
        if not self.traffic_history:
            return []
        
        current_snapshot = self.traffic_history[-1]
        
        # Apply clustering to classify congestion levels
        congestion_scores = [road['congestion_score'] for road in current_snapshot]
        
        if len(congestion_scores) > 3:
            try:
                # Use configured clustering algorithm
                clusters = self.clustering_model.fit_predict(np.array(congestion_scores).reshape(-1, 1))
                
                # Map clusters to congestion levels
                if hasattr(self.clustering_model, 'cluster_centers_'):
                    cluster_centers = self.clustering_model.cluster_centers_.flatten()
                    sorted_centers = sorted(enumerate(cluster_centers), key=lambda x: x[1])
                    
                    cluster_mapping = {}
                    for i, (cluster_idx, _) in enumerate(sorted_centers):
                        cluster_mapping[cluster_idx] = ['Low', 'Medium', 'High'][i]
                    
                    # Add cluster labels to traffic data
                    for i, road in enumerate(current_snapshot):
                        road['congestion_level'] = cluster_mapping.get(clusters[i], 'Medium')
                        road['cluster_id'] = int(clusters[i])
                else:
                    # Fallback for DBSCAN or other algorithms
                    for i, road in enumerate(current_snapshot):
                        if road['congestion_score'] < 30:
                            road['congestion_level'] = 'Low'
                        elif road['congestion_score'] < 70:
                            road['congestion_level'] = 'Medium'
                        else:
                            road['congestion_level'] = 'High'
                        road['cluster_id'] = clusters[i] if clusters[i] != -1 else 0
                        
            except Exception as e:
                print(f"Clustering error: {e}")
                # Fallback classification
                for road in current_snapshot:
                    if road['congestion_score'] < 30:
                        road['congestion_level'] = 'Low'
                    elif road['congestion_score'] < 70:
                        road['congestion_level'] = 'Medium'
                    else:
                        road['congestion_level'] = 'High'
                    road['cluster_id'] = 0
        else:
            # Fallback for small datasets
            for road in current_snapshot:
                if road['congestion_score'] < 30:
                    road['congestion_level'] = 'Low'
                elif road['congestion_score'] < 70:
                    road['congestion_level'] = 'Medium'
                else:
                    road['congestion_level'] = 'High'
                road['cluster_id'] = 0
        
        return current_snapshot
    
    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect traffic anomalies using ML"""
        if not self.traffic_history or len(self.traffic_history) < 10:
            return []
        
        current_snapshot = self.traffic_history[-1]
        anomalies = []
        
        try:
            for road_data in current_snapshot:
                features = np.array([[
                    road_data['vehicle_count'],
                    road_data['congestion_score'],
                    hash(road_data['road_type']) % 100
                ]])
                
                features_scaled = self.scaler.transform(features)
                anomaly_score = self.anomaly_detector.decision_function(features_scaled)[0]
                is_anomaly = self.anomaly_detector.predict(features_scaled)[0] == -1
                
                if is_anomaly:
                    anomalies.append({
                        'road_id': road_data['road_id'],
                        'road_name': road_data['road_name'],
                        'anomaly_score': float(anomaly_score),
                        'vehicle_count': road_data['vehicle_count'],
                        'congestion_score': road_data['congestion_score'],
                        'coordinates': road_data['coordinates'],
                        'timestamp': road_data['timestamp'],
                        'severity': 'High' if anomaly_score < -0.5 else 'Medium'
                    })
        except Exception as e:
            print(f"Error in anomaly detection: {e}")
        
        return anomalies
    
    def get_optimized_route(self, start_location: str, end_location: str) -> Dict[str, Any]:
        """Get optimized route using NetworkX with congestion weights"""
        try:
            # Find nearest nodes to start and end locations
            start_node = self._find_nearest_node(start_location)
            end_node = self._find_nearest_node(end_location)
            
            if not start_node or not end_node:
                return {
                    'error': 'Could not find valid start or end points',
                    'available_locations': self.get_available_locations()
                }
            
            # Update edge weights based on current congestion
            self._update_graph_weights()
            
            # Find shortest path considering congestion
            try:
                path = nx.shortest_path(self.graph, start_node, end_node, weight='congestion_weight')
                
                # Convert path to coordinates and road information
                route_details = []
                total_distance = 0
                total_time = 0
                
                for i in range(len(path) - 1):
                    edge_data = self.graph[path[i]][path[i + 1]]
                    
                    lat1, lon1 = map(float, path[i].split(','))
                    lat2, lon2 = map(float, path[i + 1].split(','))
                    
                    # Get current congestion for this road
                    road_id = edge_data.get('road_id', 'Unknown')
                    congestion_score = 0
                    if road_id in self.current_traffic:
                        congestion_score = self.current_traffic[road_id]['congestion_score']
                    
                    segment = {
                        'from': [lat1, lon1],
                        'to': [lat2, lon2],
                        'road_name': edge_data.get('road_name', 'Unknown Road'),
                        'road_id': road_id,
                        'distance': edge_data.get('distance', 0),
                        'congestion_score': congestion_score,
                        'estimated_time': edge_data.get('congestion_weight', 1) * 60  # Convert to seconds
                    }
                    
                    route_details.append(segment)
                    total_distance += segment['distance']
                    total_time += segment['estimated_time']
                
                return {
                    'path_coordinates': [[float(coord) for coord in node.split(',')] for node in path],
                    'route_details': route_details,
                    'total_distance': round(total_distance, 2),
                    'estimated_time': round(total_time / 60, 2),  # Convert to minutes
                    'start_node': start_node,
                    'end_node': end_node
                }
                
            except nx.NetworkXNoPath:
                return {
                    'error': 'No path found between the specified locations',
                    'start_node': start_node,
                    'end_node': end_node
                }
                
        except Exception as e:
            return {
                'error': f'Route calculation error: {str(e)}',
                'available_locations': self.get_available_locations()
            }
    
    def _find_nearest_node(self, location_name: str) -> Optional[str]:
        """Find the nearest graph node to a given location name"""
        # Simple mapping for demo purposes
        center_lat = self.config.FRONTEND_CONFIG['map_center']['lat']
        center_lng = self.config.FRONTEND_CONFIG['map_center']['lng']
        
        location_mapping = {
            'A': f'{center_lat:.4f},{center_lng:.4f}',
            'B': f'{center_lat + 0.005:.4f},{center_lng + 0.005:.4f}',
            'C': f'{center_lat + 0.002:.4f},{center_lng + 0.002:.4f}',
            'D': f'{center_lat + 0.004:.4f},{center_lng + 0.006:.4f}',
            'Main Street': f'{center_lat:.4f},{center_lng:.4f}',
            'Broadway': f'{center_lat + 0.001:.4f},{center_lng + 0.001:.4f}',
            'Park Avenue': f'{center_lat + 0.002:.4f},{center_lng + 0.002:.4f}',
            '5th Avenue': f'{center_lat + 0.003:.4f},{center_lng + 0.003:.4f}',
            'Madison Ave': f'{center_lat + 0.004:.4f},{center_lng + 0.004:.4f}'
        }
        
        if location_name in location_mapping:
            return location_mapping[location_name]
        
        # If not in mapping, try to find closest node
        nodes = list(self.graph.nodes())
        if nodes:
            return nodes[0]  # Return first node as fallback
        
        return None
    
    def _update_graph_weights(self):
        """Update graph edge weights based on current traffic congestion"""
        weight_factor = self.ml_config['route_optimization']['weight_factor']
        
        for edge in self.graph.edges(data=True):
            road_id = edge[2].get('road_id')
            base_weight = edge[2].get('distance', 1000) / 1000  # Convert to km
            
            # Default congestion multiplier
            congestion_multiplier = 1.0
            
            if road_id and road_id in self.current_traffic:
                congestion_score = self.current_traffic[road_id]['congestion_score']
                # Higher congestion = higher weight (longer travel time)
                congestion_multiplier = 1 + (congestion_score / 100) * weight_factor
            
            # Update the weight
            self.graph[edge[0]][edge[1]]['congestion_weight'] = base_weight * congestion_multiplier
    
    def get_traffic_stats(self) -> Dict[str, Any]:
        """Get comprehensive traffic statistics"""
        if not self.traffic_history:
            return {}
        
        current_snapshot = self.traffic_history[-1]
        
        # Calculate statistics
        total_vehicles = sum(road['vehicle_count'] for road in current_snapshot)
        avg_congestion = sum(road['congestion_score'] for road in current_snapshot) / len(current_snapshot)
        
        # Congestion level distribution
        congestion_levels = {'Low': 0, 'Medium': 0, 'High': 0}
        for road in current_snapshot:
            level = road.get('congestion_level', 'Medium')
            congestion_levels[level] += 1
        
        # Road type statistics
        road_type_stats = {}
        for road in current_snapshot:
            road_type = road['road_type']
            if road_type not in road_type_stats:
                road_type_stats[road_type] = {
                    'count': 0,
                    'avg_congestion': 0,
                    'total_vehicles': 0
                }
            road_type_stats[road_type]['count'] += 1
            road_type_stats[road_type]['avg_congestion'] += road['congestion_score']
            road_type_stats[road_type]['total_vehicles'] += road['vehicle_count']
        
        # Calculate averages
        for road_type in road_type_stats:
            count = road_type_stats[road_type]['count']
            road_type_stats[road_type]['avg_congestion'] = round(
                road_type_stats[road_type]['avg_congestion'] / count, 2
            )
        
        # Historical trend (last 10 snapshots)
        historical_trend = []
        for snapshot in self.traffic_history[-10:]:
            avg_congestion_snapshot = sum(road['congestion_score'] for road in snapshot) / len(snapshot)
            total_vehicles_snapshot = sum(road['vehicle_count'] for road in snapshot)
            historical_trend.append({
                'timestamp': snapshot[0]['timestamp'],
                'avg_congestion': round(avg_congestion_snapshot, 2),
                'total_vehicles': total_vehicles_snapshot
            })
        
        return {
            'current_stats': {
                'total_vehicles': total_vehicles,
                'average_congestion': round(avg_congestion, 2),
                'total_roads': len(current_snapshot),
                'timestamp': current_snapshot[0]['timestamp']
            },
            'congestion_distribution': congestion_levels,
            'road_type_stats': road_type_stats,
            'historical_trend': historical_trend,
            'anomaly_count': len(self.detect_anomalies())
        }
    
    def get_available_locations(self) -> List[str]:
        """Get list of available locations for route planning"""
        return ['A', 'B', 'C', 'D', 'Main Street', 'Broadway', 'Park Avenue', '5th Avenue', 'Madison Ave']
    
    def get_ml_status(self) -> Dict[str, Any]:
        """Get ML model status and performance metrics"""
        return {
            'clustering': {
                'algorithm': self.ml_config['clustering']['algorithm'],
                'n_clusters': self.ml_config['clustering']['n_clusters'],
                'status': 'active',
                'last_training': len(self.traffic_history)
            },
            'anomaly_detection': {
                'algorithm': self.ml_config['anomaly_detection']['algorithm'],
                'contamination': self.ml_config['anomaly_detection']['contamination'],
                'status': 'active',
                'current_anomalies': len(self.detect_anomalies())
            },
            'route_optimization': {
                'algorithm': self.ml_config['route_optimization']['algorithm'],
                'weight_factor': self.ml_config['route_optimization']['weight_factor'],
                'status': 'active',
                'graph_nodes': self.graph.number_of_nodes(),
                'graph_edges': self.graph.number_of_edges()
            },
            'data_status': {
                'total_snapshots': len(self.traffic_history),
                'current_roads': len(self.current_traffic),
                'last_update': self.traffic_history[-1][0]['timestamp'] if self.traffic_history else None
            }
        }
    
    def reset_simulation(self):
        """Reset the traffic simulation (for testing/development)"""
        self.traffic_history = []
        self.current_traffic = {}
        self._generate_initial_data()
        print("🔄 Traffic simulation reset")