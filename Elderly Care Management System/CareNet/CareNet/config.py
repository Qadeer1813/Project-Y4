DB_CONFIG = {
    'user': '',
    'password': '',
    'host': '',
    'database': 'carenet',
    'port': 3306
}
API_TOKEN = ""
API_BASE_URL = ""
API_ENDPOINTS = {
    'current_key': f"{API_BASE_URL}/current-key",
    'check_key': f"{API_BASE_URL}/check-key",
    'rotate_key': f"{API_BASE_URL}/rotate-key"
}
# Global flag for maintenance mode
MAINTENANCE_MODE = False