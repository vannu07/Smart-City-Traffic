// Smart City Traffic Management Dashboard
class TrafficDashboard {
    constructor() {
        this.apiBaseUrl = 'http://localhost:5000';
        this.map = null;
        this.trafficLayers = [];
        this.anomalyMarkers = [];
        this.routeLayer = null;
        this.charts = {};
        this.autoRefreshInterval = null;
        this.isConnected = false;
        
        this.init();
    }
    
    async init() {
        this.showLoading(true);
        this.initializeMap();
        this.initializeCharts();
        this.setupEventListeners();
        
        // Initial data load
        await this.loadAllData();
        
        // Start auto-refresh if enabled
        this.setupAutoRefresh();
        
        this.showLoading(false);
    }
    
    initializeMap() {
        // Initialize Leaflet map centered on NYC area
        this.map = L.map('map').setView([40.7128, -74.0060], 13);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(this.map);
        
        // Add custom map controls
        this.addMapControls();
    }
    
    addMapControls() {
        // Custom control for map legend
        const legendControl = L.control({ position: 'bottomright' });
        legendControl.onAdd = function() {
            const div = L.DomUtil.create('div', 'leaflet-control-legend');
            div.innerHTML = `
                <div style="background: rgba(255,255,255,0.9); padding: 10px; border-radius: 8px; font-size: 12px;">
                    <strong>Traffic Levels</strong><br>
                    <span style="color: #2ed573;">●</span> Low Congestion<br>
                    <span style="color: #ffa502;">●</span> Medium Congestion<br>
                    <span style="color: #ff4757;">●</span> High Congestion<br>
                    <span style="color: #8b00ff;">⚠</span> Anomaly Alert
                </div>
            `;
            return div;
        };
        legendControl.addTo(this.map);
    }
    
    initializeCharts() {
        // Congestion Distribution Chart (Doughnut)
        const congestionCtx = document.getElementById('congestionChart').getContext('2d');
        this.charts.congestion = new Chart(congestionCtx, {
            type: 'doughnut',
            data: {
                labels: ['Low', 'Medium', 'High'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: ['#2ed573', '#ffa502', '#ff4757'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
        
        // Traffic Trend Chart (Line)
        const trendCtx = document.getElementById('trendChart').getContext('2d');
        this.charts.trend = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Avg Congestion',
                    data: [],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Congestion %'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    setupEventListeners() {
        // Route finder button
        document.getElementById('findRouteBtn').addEventListener('click', () => {
            this.findOptimalRoute();
        });
        
        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadAllData();
        });
        
        // Auto-refresh toggle
        document.getElementById('autoRefresh').addEventListener('change', (e) => {
            this.setupAutoRefresh(e.target.checked);
        });
    }
    
    setupAutoRefresh(enabled = true) {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
        
        if (enabled) {
            this.autoRefreshInterval = setInterval(() => {
                this.loadAllData();
            }, 10000); // Refresh every 10 seconds
        }
    }
    
    async loadAllData() {
        try {
            this.updateConnectionStatus('connecting');
            
            // Load all data concurrently
            const [trafficData, anomaliesData, statsData] = await Promise.all([
                this.fetchTrafficData(),
                this.fetchAnomalies(),
                this.fetchStats()
            ]);
            
            // Update UI components
            this.updateTrafficMap(trafficData);
            this.updateAnomalies(anomaliesData);
            this.updateStats(statsData);
            this.updateTrafficTable(trafficData);
            
            this.updateConnectionStatus('connected');
            
        } catch (error) {
            console.error('Error loading data:', error);
            this.updateConnectionStatus('error');
            this.showError('Failed to load traffic data. Please check if the backend server is running.');
        }
    }
    
    async fetchTrafficData() {
        const response = await fetch(`${this.apiBaseUrl}/traffic`);
        if (!response.ok) throw new Error('Failed to fetch traffic data');
        const result = await response.json();
        return result.data || [];
    }
    
    async fetchAnomalies() {
        const response = await fetch(`${this.apiBaseUrl}/anomalies`);
        if (!response.ok) throw new Error('Failed to fetch anomalies');
        const result = await response.json();
        return result.anomalies || [];
    }
    
    async fetchStats() {
        const response = await fetch(`${this.apiBaseUrl}/stats`);
        if (!response.ok) throw new Error('Failed to fetch stats');
        const result = await response.json();
        return result.stats || {};
    }
    
    updateTrafficMap(trafficData) {
        // Clear existing traffic layers
        this.trafficLayers.forEach(layer => this.map.removeLayer(layer));
        this.trafficLayers = [];
        
        // Add traffic segments to map
        trafficData.forEach(road => {
            const color = this.getCongestionColor(road.congestion_level);
            const weight = this.getCongestionWeight(road.congestion_level);
            
            const polyline = L.polyline([
                road.coordinates.start,
                road.coordinates.end
            ], {
                color: color,
                weight: weight,
                opacity: 0.8
            }).addTo(this.map);
            
            // Add popup with road information
            polyline.bindPopup(`
                <div style="font-family: inherit;">
                    <h4 style="margin: 0 0 8px 0; color: #333;">${road.road_name}</h4>
                    <p style="margin: 4px 0;"><strong>Vehicles:</strong> ${road.vehicle_count}</p>
                    <p style="margin: 4px 0;"><strong>Congestion:</strong> ${road.congestion_score}%</p>
                    <p style="margin: 4px 0;"><strong>Level:</strong> 
                        <span style="color: ${color}; font-weight: bold;">${road.congestion_level}</span>
                    </p>
                    <p style="margin: 4px 0; font-size: 12px; color: #666;">
                        ${new Date(road.timestamp).toLocaleTimeString()}
                    </p>
                </div>
            `);
            
            this.trafficLayers.push(polyline);
        });
    }
    
    updateAnomalies(anomaliesData) {
        // Clear existing anomaly markers
        this.anomalyMarkers.forEach(marker => this.map.removeLayer(marker));
        this.anomalyMarkers = [];
        
        // Add anomaly markers
        anomaliesData.forEach(anomaly => {
            const center = [
                (anomaly.coordinates.start[0] + anomaly.coordinates.end[0]) / 2,
                (anomaly.coordinates.start[1] + anomaly.coordinates.end[1]) / 2
            ];
            
            const marker = L.marker(center, {
                icon: L.divIcon({
                    className: 'anomaly-marker',
                    html: '<i class="fas fa-exclamation-triangle" style="color: #8b00ff; font-size: 20px;"></i>',
                    iconSize: [30, 30],
                    iconAnchor: [15, 15]
                })
            }).addTo(this.map);
            
            marker.bindPopup(`
                <div style="font-family: inherit;">
                    <h4 style="margin: 0 0 8px 0; color: #8b00ff;">⚠ Traffic Anomaly</h4>
                    <p style="margin: 4px 0;"><strong>Location:</strong> ${anomaly.road_name}</p>
                    <p style="margin: 4px 0;"><strong>Severity:</strong> ${anomaly.severity}</p>
                    <p style="margin: 4px 0;"><strong>Vehicles:</strong> ${anomaly.vehicle_count}</p>
                    <p style="margin: 4px 0;"><strong>Congestion:</strong> ${anomaly.congestion_score}%</p>
                    <p style="margin: 4px 0; font-size: 12px; color: #666;">
                        Detected: ${new Date(anomaly.timestamp).toLocaleTimeString()}
                    </p>
                </div>
            `);
            
            this.anomalyMarkers.push(marker);
        });
        
        // Update alerts panel
        this.updateAlertsPanel(anomaliesData);
    }
    
    updateStats(statsData) {
        if (!statsData.current_stats) return;
        
        const currentStats = statsData.current_stats;
        
        // Update key metrics
        document.getElementById('totalVehicles').textContent = currentStats.total_vehicles || '-';
        document.getElementById('avgCongestion').textContent = 
            currentStats.average_congestion ? `${currentStats.average_congestion}%` : '-';
        document.getElementById('anomalyCount').textContent = statsData.anomaly_count || '0';
        
        // Update congestion distribution chart
        if (statsData.congestion_distribution) {
            const distribution = statsData.congestion_distribution;
            this.charts.congestion.data.datasets[0].data = [
                distribution.Low || 0,
                distribution.Medium || 0,
                distribution.High || 0
            ];
            this.charts.congestion.update();
        }
        
        // Update trend chart
        if (statsData.historical_trend) {
            const trend = statsData.historical_trend;
            this.charts.trend.data.labels = trend.map(point => 
                new Date(point.timestamp).toLocaleTimeString()
            );
            this.charts.trend.data.datasets[0].data = trend.map(point => 
                point.avg_congestion
            );
            this.charts.trend.update();
        }
    }
    
    updateTrafficTable(trafficData) {
        const tbody = document.getElementById('trafficTableBody');
        tbody.innerHTML = '';
        
        // Sort by congestion score (highest first)
        const sortedData = [...trafficData].sort((a, b) => b.congestion_score - a.congestion_score);
        
        sortedData.forEach(road => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${road.road_name}</td>
                <td>${road.vehicle_count}</td>
                <td>${road.congestion_score}%</td>
                <td>
                    <span class="congestion-badge ${road.congestion_level.toLowerCase()}">
                        ${road.congestion_level}
                    </span>
                </td>
                <td>
                    <i class="fas fa-circle" style="color: ${this.getCongestionColor(road.congestion_level)};"></i>
                    Active
                </td>
            `;
            tbody.appendChild(row);
        });
    }
    
    updateAlertsPanel(anomaliesData) {
        const container = document.getElementById('alertsContainer');
        container.innerHTML = '';
        
        if (anomaliesData.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: #666;">
                    <i class="fas fa-check-circle" style="font-size: 2rem; color: #2ed573; margin-bottom: 1rem;"></i>
                    <p>No traffic anomalies detected</p>
                </div>
            `;
            return;
        }
        
        anomaliesData.forEach(anomaly => {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert-item ${anomaly.severity.toLowerCase()}-severity`;
            alertDiv.innerHTML = `
                <div class="alert-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <div class="alert-content">
                    <div class="alert-title">Traffic Anomaly Detected</div>
                    <div class="alert-description">
                        Unusual traffic pattern on ${anomaly.road_name} - 
                        ${anomaly.vehicle_count} vehicles (${anomaly.congestion_score}% congestion)
                    </div>
                    <div class="alert-meta">
                        Severity: ${anomaly.severity} | 
                        Detected: ${new Date(anomaly.timestamp).toLocaleString()}
                    </div>
                </div>
            `;
            container.appendChild(alertDiv);
        });
    }
    
    async findOptimalRoute() {
        const startLocation = document.getElementById('startLocation').value;
        const endLocation = document.getElementById('endLocation').value;
        
        if (startLocation === endLocation) {
            this.showError('Please select different start and end locations.');
            return;
        }
        
        try {
            this.showLoading(true, 'Calculating optimal route...');
            
            const response = await fetch(
                `${this.apiBaseUrl}/route?start=${encodeURIComponent(startLocation)}&end=${encodeURIComponent(endLocation)}`
            );
            
            if (!response.ok) throw new Error('Failed to calculate route');
            
            const result = await response.json();
            
            if (result.status === 'error') {
                throw new Error(result.message);
            }
            
            this.displayRoute(result.route);
            this.showLoading(false);
            
        } catch (error) {
            console.error('Route calculation error:', error);
            this.showError(`Failed to calculate route: ${error.message}`);
            this.showLoading(false);
        }
    }
    
    displayRoute(routeData) {
        // Clear existing route
        if (this.routeLayer) {
            this.map.removeLayer(this.routeLayer);
        }
        
        if (routeData.error) {
            this.showError(routeData.error);
            return;
        }
        
        // Draw route on map
        if (routeData.path_coordinates && routeData.path_coordinates.length > 0) {
            this.routeLayer = L.polyline(routeData.path_coordinates, {
                color: '#667eea',
                weight: 6,
                opacity: 0.8,
                dashArray: '10, 10'
            }).addTo(this.map);
            
            // Fit map to route bounds
            this.map.fitBounds(this.routeLayer.getBounds(), { padding: [20, 20] });
            
            // Add start and end markers
            if (routeData.path_coordinates.length >= 2) {
                const startCoord = routeData.path_coordinates[0];
                const endCoord = routeData.path_coordinates[routeData.path_coordinates.length - 1];
                
                L.marker(startCoord, {
                    icon: L.divIcon({
                        className: 'route-marker',
                        html: '<div style="background: #2ed573; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; font-weight: bold;">S</div>',
                        iconSize: [30, 30],
                        iconAnchor: [15, 15]
                    })
                }).addTo(this.map).bindPopup('Start Location');
                
                L.marker(endCoord, {
                    icon: L.divIcon({
                        className: 'route-marker',
                        html: '<div style="background: #ff4757; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; font-weight: bold;">E</div>',
                        iconSize: [30, 30],
                        iconAnchor: [15, 15]
                    })
                }).addTo(this.map).bindPopup('End Location');
            }
        }
        
        // Update route info panel
        const routeInfo = document.getElementById('routeInfo');
        const routeDistance = document.getElementById('routeDistance');
        const routeTime = document.getElementById('routeTime');
        
        if (routeData.total_distance && routeData.estimated_time) {
            routeDistance.textContent = `${(routeData.total_distance / 1000).toFixed(2)} km`;
            routeTime.textContent = `${routeData.estimated_time.toFixed(1)} min`;
            routeInfo.classList.remove('hidden');
        } else {
            routeInfo.classList.add('hidden');
        }
    }
    
    getCongestionColor(level) {
        const colors = {
            'Low': '#2ed573',
            'Medium': '#ffa502',
            'High': '#ff4757'
        };
        return colors[level] || '#666';
    }
    
    getCongestionWeight(level) {
        const weights = {
            'Low': 4,
            'Medium': 6,
            'High': 8
        };
        return weights[level] || 5;
    }
    
    updateConnectionStatus(status) {
        const statusDot = document.getElementById('connectionStatus');
        const statusText = document.getElementById('statusText');
        
        statusDot.className = `status-dot ${status}`;
        
        switch (status) {
            case 'connected':
                statusText.textContent = 'Connected';
                this.isConnected = true;
                break;
            case 'connecting':
                statusText.textContent = 'Connecting...';
                this.isConnected = false;
                break;
            case 'error':
                statusText.textContent = 'Connection Error';
                this.isConnected = false;
                break;
        }
    }
    
    showLoading(show, message = 'Loading traffic data...') {
        const overlay = document.getElementById('loadingOverlay');
        const text = overlay.querySelector('p');
        
        text.textContent = message;
        
        if (show) {
            overlay.classList.remove('hidden');
        } else {
            overlay.classList.add('hidden');
        }
    }
    
    showError(message) {
        // Create a temporary error notification
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #ff4757;
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(255, 71, 87, 0.3);
            z-index: 10000;
            max-width: 400px;
            font-weight: 500;
        `;
        errorDiv.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <i class="fas fa-exclamation-circle"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(errorDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.trafficDashboard = new TrafficDashboard();
});

// Handle page visibility changes to pause/resume auto-refresh
document.addEventListener('visibilitychange', () => {
    if (window.trafficDashboard) {
        const isVisible = !document.hidden;
        const autoRefreshEnabled = document.getElementById('autoRefresh').checked;
        window.trafficDashboard.setupAutoRefresh(isVisible && autoRefreshEnabled);
    }
});