"""
Smart City Traffic Management System Configuration

This module contains all configuration settings for the application,
including environment variables, API settings, and ML model parameters.
"""

import os
from typing import Dict, Any

class Config:
    """Main configuration class for the Smart City Traffic Management System"""

    def __init__(self):
        """Initialize configuration from environment variables"""
        self.load_environment()

    def load_environment(self):
        """Load configuration from environment variables with defaults"""

        # === SERVER CONFIGURATION ===
        self.ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
        self.DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
        self.HOST = os.getenv('HOST', '0.0.0.0')
        self.PORT = int(os.getenv('PORT', 5000))

        # === API CONFIGURATION ===
        self.API_PREFIX = os.getenv('API_PREFIX', '/api')
        self.API_VERSION = os.getenv('API_VERSION', 'v1')
        self.CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

        # === TRAFFIC SIMULATION SETTINGS ===
        self.AUTO_REFRESH_INTERVAL = int(os.getenv('AUTO_REFRESH_INTERVAL', 5))
        self.SIMULATION_SPEED = float(os.getenv('SIMULATION_SPEED', 1.0))
        self.MAX_HISTORY_RECORDS = int(os.getenv('MAX_HISTORY_RECORDS', 200))

        # === ML MODEL CONFIGURATION ===
        self.ML_CONFIG = {
            'clustering': {
                'algorithm': os.getenv('CLUSTERING_ALGORITHM', 'kmeans'),
                'n_clusters': int(os.getenv('CLUSTERING_N_CLUSTERS', 3)),
                'random_state': int(os.getenv('CLUSTERING_RANDOM_STATE', 42))
            },
            'anomaly_detection': {
                'algorithm': os.getenv('ANOMALY_ALGORITHM', 'isolation_forest'),
                'contamination': float(os.getenv('ANOMALY_CONTAMINATION', 0.1)),
                'random_state': int(os.getenv('ANOMALY_RANDOM_STATE', 42))
            },
            'route_optimization': {
                'algorithm': os.getenv('ROUTE_ALGORITHM', 'shortest_path'),
                'weight_factor': float(os.getenv('ROUTE_WEIGHT_FACTOR', 2.0))
            }
        }

        # === EXTERNAL API CONFIGURATION ===
        # Google Maps API (optional - for real GPS data)
        self.GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')
        self.GOOGLE_MAPS_ENABLED = bool(self.GOOGLE_MAPS_API_KEY)

        # OpenWeather API (optional - for weather-based traffic analysis)
        self.OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '')
        self.OPENWEATHER_ENABLED = bool(self.OPENWEATHER_API_KEY)

        # Traffic API (optional - for real traffic data)
        self.TRAFFIC_API_KEY = os.getenv('TRAFFIC_API_KEY', '')
        self.TRAFFIC_API_ENABLED = bool(self.TRAFFIC_API_KEY)

        # === DATABASE CONFIGURATION ===
        self.DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///traffic_data.db')
        self.DATABASE_ENABLED = os.getenv('DATABASE_ENABLED', 'False').lower() == 'true'

        # === LOGGING CONFIGURATION ===
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', 'logs/traffic_system.log')

        # === SECURITY CONFIGURATION ===
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        self.API_RATE_LIMIT = os.getenv('API_RATE_LIMIT', '100/hour')

        # === FRONTEND CONFIGURATION ===
        self.FRONTEND_CONFIG = {
            'map_center': {
                'lat': float(os.getenv('MAP_CENTER_LAT', 40.7128)),
                'lng': float(os.getenv('MAP_CENTER_LNG', -74.0060))
            },
            'map_zoom': int(os.getenv('MAP_ZOOM', 13)),
            'auto_refresh_frontend': int(os.getenv('FRONTEND_REFRESH_INTERVAL', 10)),
            'theme': os.getenv('FRONTEND_THEME', 'auto')  # auto, light, dark
        }

        # === NOTIFICATION CONFIGURATION ===
        self.NOTIFICATIONS = {
            'email_enabled': os.getenv('EMAIL_NOTIFICATIONS', 'False').lower() == 'true',
            'email_smtp_server': os.getenv('EMAIL_SMTP_SERVER', ''),
            'email_smtp_port': int(os.getenv('EMAIL_SMTP_PORT', 587)),
            'email_username': os.getenv('EMAIL_USERNAME', ''),
            'email_password': os.getenv('EMAIL_PASSWORD', ''),
            'alert_threshold': float(os.getenv('ALERT_THRESHOLD', 80.0))
        }

    def get_api_config(self) -> Dict[str, Any]:
        """Get API-specific configuration"""
        return {
            'google_maps': {
                'enabled': self.GOOGLE_MAPS_ENABLED,
                'api_key': self.GOOGLE_MAPS_API_KEY,
                'description': 'Real-time GPS and traffic data from Google Maps'
            },
            'openweather': {
                'enabled': self.OPENWEATHER_ENABLED,
                'api_key': self.OPENWEATHER_API_KEY,
                'description': 'Weather data for traffic pattern analysis'
            },
            'traffic_api': {
                'enabled': self.TRAFFIC_API_ENABLED,
                'api_key': self.TRAFFIC_API_KEY,
                'description': 'Real-time traffic data from external providers'
            },
            'simulation': {
                'enabled': True,
                'description': 'Built-in traffic simulation (no API key required)'
            }
        }

    def get_ml_config(self) -> Dict[str, Any]:
        """Get ML model configuration"""
        return self.ML_CONFIG

    def get_frontend_config(self) -> Dict[str, Any]:
        """Get frontend configuration for JavaScript"""
        return {
            'api_base_url': f"http://{self.HOST}:{self.PORT}{self.API_PREFIX}",
            'map_config': self.FRONTEND_CONFIG,
            'auto_refresh_interval': self.FRONTEND_CONFIG['auto_refresh_frontend'] * 1000,  # Convert to ms
            'theme': self.FRONTEND_CONFIG['theme']
        }

    def validate_config(self) -> Dict[str, str]:
        """Validate configuration and return any warnings or errors"""
        warnings = []
        errors = []

        # Check for production settings
        if self.ENVIRONMENT == 'production':
            if self.SECRET_KEY == 'dev-secret-key-change-in-production':
                errors.append("SECRET_KEY must be changed in production")
            if self.DEBUG:
                warnings.append("DEBUG should be False in production")

        # Check API keys
        if not any([self.GOOGLE_MAPS_ENABLED, self.TRAFFIC_API_ENABLED]):
            warnings.append("No external APIs configured - using simulation data only")

        # Check database
        if not self.DATABASE_ENABLED:
            warnings.append("Database not enabled - data will not be persisted")

        return {
            'warnings': warnings,
            'errors': errors,
            'status': 'error' if errors else 'warning' if warnings else 'ok'
        }

    def __str__(self) -> str:
        """String representation of configuration"""
        return f"Config(env={self.ENVIRONMENT}, host={self.HOST}:{self.PORT}, debug={self.DEBUG})"

# Development configuration
class DevelopmentConfig(Config):
    """Development-specific configuration"""
    def __init__(self):
        super().__init__()
        self.DEBUG = True
        self.LOG_LEVEL = 'DEBUG'

# Production configuration
class ProductionConfig(Config):
    """Production-specific configuration"""
    def __init__(self):
        super().__init__()
        self.DEBUG = False
        self.LOG_LEVEL = 'WARNING'

# Testing configuration
class TestingConfig(Config):
    """Testing-specific configuration"""
    def __init__(self):
        super().__init__()
        self.DEBUG = True
        self.DATABASE_URL = 'sqlite:///:memory:'
        self.AUTO_REFRESH_INTERVAL = 1  # Faster for testing

# Configuration factory
def get_config(environment: str = None) -> Config:
    """Get configuration based on environment"""
    env = environment or os.getenv('ENVIRONMENT', 'development')

    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }

    return configs.get(env, Config)()
