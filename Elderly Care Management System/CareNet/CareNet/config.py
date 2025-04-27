DB_CONFIG = {
    'user': 'root',
    'password': 'Qadeerh03',
    'host': 'localhost',
    'database': 'carenet',
    'port': 3306
}
API_TOKEN = "TPM2HgNtx7snEu5m3rC_9py4YCwiB_9rt_tm616whPM"
API_BASE_URL = "http://localhost:8001"
API_ENDPOINTS = {
    'current_key': f"{API_BASE_URL}/current-key",
    'check_key': f"{API_BASE_URL}/check-key",
    'rotate_key': f"{API_BASE_URL}/rotate-key"
}
# Global flag for maintenance mode
MAINTENANCE_MODE = False