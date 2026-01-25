"""
Smart City Traffic Management System - Utility Functions

This module contains helper functions and utilities used across the application.
"""

import os
import re
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

def load_env_file(env_path: str = '.env') -> Dict[str, str]:
    """Load environment variables from .env file"""
    env_vars = {}

    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()

    return env_vars

def format_timestamp(timestamp: Optional[str] = None) -> str:
    """Format timestamp for display"""
    if timestamp is None:
        timestamp = datetime.now().isoformat()

    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return timestamp

def calculate_distance(coord1: List[float], coord2: List[float]) -> float:
    """Calculate distance between two coordinates (simplified)"""
    import math

    lat1, lon1 = coord1
    lat2, lon2 = coord2

    # Haversine formula (simplified for small distances)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat/2) * math.sin(dlat/2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon/2) * math.sin(dlon/2))

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    # Earth's radius in meters
    earth_radius = 6371000

    return earth_radius * c

def validate_coordinates(coordinates: Dict[str, List[float]]) -> bool:
    """Validate coordinate format"""
    try:
        start = coordinates.get('start', [])
        end = coordinates.get('end', [])

        if len(start) != 2 or len(end) != 2:
            return False

        # Check if coordinates are within reasonable bounds
        for coord in [start, end]:
            lat, lon = coord
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                return False

        return True
    except Exception:
        return False


def create_response(status: str = 'success', data: Any = None,
                   message: str = None, **kwargs) -> Dict[str, Any]:
    """Create standardized API response"""
    response = {
        'status': status,
        'timestamp': time.time()
    }

    if data is not None:
        response['data'] = data

    if message:
        response['message'] = message

    # Add any additional fields
    response.update(kwargs)

    return response

def log_api_call(endpoint: str, method: str, status_code: int,
                response_time: float = None):
    """Log API call for monitoring"""
    # In a production environment, this would write to a proper logging system
    if response_time:
        print(f"API: {method} {endpoint} -> {status_code} ({response_time:.3f}s)")
    else:
        print(f"API: {method} {endpoint} -> {status_code}")

def sanitize_location_name(location: str) -> str:
    """Sanitize location name for safe processing"""
    if not location:
        return ""

    # Remove special characters and normalize
    sanitized = re.sub(r'[^a-zA-Z0-9\s\-_]', '', location)
    return sanitized.strip()

def calculate_congestion_level(congestion_score: float) -> str:
    """Calculate congestion level from score"""
    if congestion_score < 30:
        return 'Low'
    if congestion_score < 70:
        return 'Medium'
    return 'High'

def get_color_for_congestion(level: str) -> str:
    """Get color code for congestion level"""
    colors = {
        'Low': '#2ed573',
        'Medium': '#ffa502',
        'High': '#ff4757'
    }
    return colors.get(level, '#666666')

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    import math

    if size_bytes == 0:
        return "0B"

    size_names = ["B", "KB", "MB", "GB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)

    return f"{s} {size_names[i]}"

def check_system_health() -> Dict[str, Any]:
    """Check system health metrics"""
    import psutil

    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)

        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent

        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100

        return {
            'cpu_usage': cpu_percent,
            'memory_usage': memory_percent,
            'disk_usage': disk_percent,
            'status': 'healthy' if all([
                cpu_percent < 80,
                memory_percent < 80,
                disk_percent < 90
            ]) else 'warning'
        }
    except ImportError:
        # psutil not available
        return {
            'status': 'unknown',
            'message': 'System monitoring not available'
        }

def generate_api_key(length: int = 32) -> str:
    """Generate a random API key"""
    import secrets
    import string

    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def validate_api_key(api_key: str, valid_keys: List[str]) -> bool:
    """Validate API key"""
    return api_key in valid_keys if api_key and valid_keys else True

def rate_limit_check(client_id: str, limit: int = 100,
                    window: int = 3600) -> Dict[str, Any]:
    """Simple rate limiting check"""
    # This is a simplified implementation
    # In production, you'd use Redis or similar
    # Note: client_id parameter is for future extension

    current_time = time.time()

    # For demo purposes, always allow
    return {
        'allowed': True,
        'remaining': limit - 1,
        'reset_time': current_time + window
    }

class ConfigValidator:
    """Configuration validation utility"""

    @staticmethod
    def validate_required_fields(config: Dict[str, Any],
                                required_fields: List[str]) -> List[str]:
        """Validate required configuration fields"""
        missing_fields = []

        for field in required_fields:
            if field not in config or config[field] is None:
                missing_fields.append(field)

        return missing_fields

    @staticmethod
    def validate_port(port: Any) -> bool:
        """Validate port number"""
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        return url_pattern.match(url) is not None
