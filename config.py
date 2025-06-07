# Business search configuration
SEARCH_TERMS = [
    "restaurants",
    "hotels",
    "cafes",
    "bars",
    "shops"  # Add more search terms as needed
]

# Target locations in Kenya
LOCATIONS = [
    "Nairobi, Kenya",
    "Mombasa, Kenya",
    "Kisumu, Kenya",
    
]

# Scraping parameters
MAX_RESULTS = 100  # Increased from 30 for more comprehensive results
MIN_DELAY = 4.0    # Slightly increased to avoid rate limiting
MAX_DELAY = 8.0
MAX_RETRIES = 5    # Increased for better reliability
REQUEST_TIMEOUT = 30  # New timeout parameter in seconds

# Search filters
MIN_RATING = 3.5
REQUIRE_NO_WEBSITE = True
EXCLUDE_CHAINS = True  # New parameter to filter out chain businesses
MIN_REVIEWS = 3      # New parameter for minimum number of reviews
BUSINESS_TYPES = [    # New parameter to filter by business type
    "restaurant",
    "hotel",
    "bar"
]

# Output settings
OUTPUT_FILE = "kenya_businesses.csv"  # More descriptive filename
LOGS_DIR = "logs"
ERROR_LOG = "error_log.txt"          # New separate error log file

# Search parameters
RADIUS_KM = 30
MAX_PRICE_LEVEL = 4   # New parameter for price level filter (1-4)
SORT_BY = "rating"    # New parameter: "rating" or "reviews"

# Advanced settings
ENABLE_PROXY = False  # New parameter for proxy support
VERIFY_SSL = True     # New parameter for SSL verification
DEBUG_MODE = False    # New parameter for debugging
SAVE_HTML = False     # New parameter to save raw HTML responses
# ...existing code...

# Elasticsearch settings
ELASTICSEARCH_HOSTS = ["http://localhost:9200"]  # Default Elasticsearch port
ELASTICSEARCH_USERNAME = ""  # If authentication is needed
ELASTICSEARCH_PASSWORD = ""  # If authentication is needed