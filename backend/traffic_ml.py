"""
Smart City Traffic Management System - Machine Learning Module

This module contains traffic simulation and ML models for traffic analysis.
"""

import random

import networkx as nx
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class TrafficMLSystem:
    """Machine Learning system for traffic management"""

    def __init__(self):
        self.road_segments = self._initialize_road_network()
        self.traffic_history = []
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.graph = self._create_road_graph()
        self.current_traffic = {}

        # Initialize with some historical data for ML models
        self._generate_initial_data()

    def _initialize_road_network(self):
        """Initialize simulated road network for a smart city"""
        # Simulated city grid with major roads and intersections
        roads = [
            {"id": "R001", "name": "Main Street", "start": [40.7128, -74.0060], "end": [40.7138, -74.0050], "type": "arterial"},
            {"id": "R002", "name": "Broadway", "start": [40.7138, -74.0050], "end": [40.7148, -74.0040], "type": "arterial"},
            {"id": "R003", "name": "Park Avenue", "start": [40.7148, -74.0040], "end": [40.7158, -74.0030], "type": "arterial"},
            {"id": "R004", "name": "5th Avenue", "start": [40.7158, -74.0030], "end": [40.7168, -74.0020], "type": "arterial"},
            {"id": "R005", "name": "Madison Ave", "start": [40.7168, -74.0020], "end": [40.7178, -74.0010], "type": "arterial"},

            # Cross streets
            {"id": "R006", "name": "42nd Street", "start": [40.7128, -74.0060], "end": [40.7128, -74.0000], "type": "collector"},
            {"id": "R007", "name": "34th Street", "start": [40.7138, -74.0050], "end": [40.7138, -74.0010], "type": "collector"},
            {"id": "R008", "name": "23rd Street", "start": [40.7148, -74.0040], "end": [40.7148, -74.0000], "type": "collector"},
            {"id": "R009", "name": "14th Street", "start": [40.7158, -74.0030], "end": [40.7158, -74.0010], "type": "collector"},
            {"id": "R010", "name": "Houston St", "start": [40.7168, -74.0020], "end": [40.7168, -74.0000], "type": "collector"},

            # Local roads
            {"id": "R011", "name": "1st Avenue", "start": [40.7128, -74.0000], "end": [40.7178, -74.0000], "type": "local"},
            {"id": "R012", "name": "2nd Avenue", "start": [40.7128, -74.0010], "end": [40.7178, -74.0010], "type": "local"},
            {"id": "R013", "name": "3rd Avenue", "start": [40.7128, -74.0020], "end": [40.7178, -74.0020], "type": "local"},
            {"id": "R014", "name": "Lexington Ave", "start": [40.7128, -74.0030], "end": [40.7178, -74.0030], "type": "local"},
            {"id": "R015", "name": "Park Ave South", "start": [40.7128, -74.0040], "end": [40.7178, -74.0040], "type": "local"},
        ]
        return roads

    def _create_road_graph(self):
        """Create NetworkX graph for route optimization"""
        graph = nx.Graph()

        # Add nodes (intersections)
        intersections = set()
        for road in self.road_segments:
            start_node = f"{road['start'][0]:.4f},{road['start'][1]:.4f}"
            end_node = f"{road['end'][0]:.4f},{road['end'][1]:.4f}"
            intersections.add(start_node)
            intersections.add(end_node)

        for intersection in intersections:
            lat, lon = map(float, intersection.split(','))
            graph.add_node(intersection, pos=(lat, lon))

        # Add edges (roads)
        for road in self.road_segments:
            start_node = f"{road['start'][0]:.4f},{road['start'][1]:.4f}"
            end_node = f"{road['end'][0]:.4f},{road['end'][1]:.4f}"

            # Calculate distance (simplified)
            distance = np.sqrt(
                (road['end'][0] - road['start'][0])**2 +
                (road['end'][1] - road['start'][1])**2
            ) * 111000  # Convert to meters approximately

            graph.add_edge(start_node, end_node,
                          road_id=road['id'],
                          distance=distance,
                          road_name=road['name'],
                          road_type=road['type'])

        return graph

    def _generate_initial_data(self):
        """Generate initial traffic data for ML model training"""
        for _ in range(100):  # Generate 100 historical data points
            traffic_data = self._simulate_traffic_snapshot()
            self.traffic_history.append(traffic_data)

        # Train initial models
        self._train_anomaly_detector()

    def _simulate_traffic_snapshot(self):
        """Simulate a single traffic data snapshot"""
        current_time = datetime.now()
        hour = current_time.hour

        # Time-based traffic patterns
        rush_hour_multiplier = 1.0
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
            rush_hour_multiplier = 2.5
        elif 22 <= hour or hour <= 6:  # Night time
            rush_hour_multiplier = 0.3

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

    def _train_anomaly_detector(self):
        """Train the anomaly detection model"""
        if len(self.traffic_history) < 10:
            return

        # Prepare features for anomaly detection
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
            features_scaled = self.scaler.fit_transform(features_array)
            self.anomaly_detector.fit(features_scaled)

    def update_traffic_simulation(self):
        """Update traffic simulation (called by background thread)"""
        new_snapshot = self._simulate_traffic_snapshot()
        self.traffic_history.append(new_snapshot)

        # Keep only last 200 snapshots to manage memory
        if len(self.traffic_history) > 200:
            self.traffic_history = self.traffic_history[-200:]

        # Update current traffic data
        self.current_traffic = {road['road_id']: road for road in new_snapshot}

        # Retrain anomaly detector periodically
        if len(self.traffic_history) % 20 == 0:
            self._train_anomaly_detector()

    def get_current_traffic(self):
        """Get current traffic data with clustering"""
        if not self.traffic_history:
            return []

        current_snapshot = self.traffic_history[-1]

        # Apply clustering to classify congestion levels
        congestion_scores = [road['congestion_score'] for road in current_snapshot]

        if len(congestion_scores) > 3:
            # Use KMeans clustering to classify into Low/Medium/High
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(np.array(congestion_scores).reshape(-1, 1))

            # Map clusters to congestion levels
            cluster_centers = kmeans.cluster_centers_.flatten()
            sorted_centers = sorted(enumerate(cluster_centers), key=lambda x: x[1])

            cluster_mapping = {}
            for i, (cluster_idx, _) in enumerate(sorted_centers):
                cluster_mapping[cluster_idx] = ['Low', 'Medium', 'High'][i]

            # Add cluster labels to traffic data
            for i, road in enumerate(current_snapshot):
                road['congestion_level'] = cluster_mapping[clusters[i]]
                road['cluster_id'] = int(clusters[i])
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

    def detect_anomalies(self):
        """Detect traffic anomalies using Isolation Forest"""
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
        except Exception:
            print("Error in anomaly detection")

        return anomalies

    def get_optimized_route(self, start_location, end_location):
        """Get optimized route using NetworkX shortest path with congestion weights"""
        try:
            # Find nearest nodes to start and end locations
            start_node = self._find_nearest_node(start_location)
            end_node = self._find_nearest_node(end_location)

            if not start_node or not end_node:
                return {
                    'error': 'Could not find valid start or end points',
                    'available_locations': list(self.graph.nodes())
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

        except Exception:
            return {
                'error': 'Route calculation error. Please try again later.',
                'available_locations': list(self.graph.nodes())
            }

    def _find_nearest_node(self, location_name):
        """Find the nearest graph node to a given location name or coordinates"""
        # Simple mapping for demo purposes
        location_mapping = {
            'A': '40.7128,-74.0060',  # Main Street start
            'B': '40.7178,-74.0010',  # Madison Ave end
            'C': '40.7148,-74.0040',  # Park Avenue start
            'D': '40.7168,-74.0000',  # Houston St end
            'Main Street': '40.7128,-74.0060',
            'Broadway': '40.7138,-74.0050',
            'Park Avenue': '40.7148,-74.0040',
            '5th Avenue': '40.7158,-74.0030',
            'Madison Ave': '40.7168,-74.0020'
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
        for edge in self.graph.edges(data=True):
            road_id = edge[2].get('road_id')
            base_weight = edge[2].get('distance', 1000) / 1000  # Convert to km

            # Default congestion multiplier
            congestion_multiplier = 1.0

            if road_id and road_id in self.current_traffic:
                congestion_score = self.current_traffic[road_id]['congestion_score']
                # Higher congestion = higher weight (longer travel time)
                congestion_multiplier = 1 + (congestion_score / 100) * 2  # 1x to 3x multiplier

            # Update the weight
            self.graph[edge[0]][edge[1]]['congestion_weight'] = base_weight * congestion_multiplier

    def get_traffic_stats(self):
        """Get traffic statistics and metrics"""
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
