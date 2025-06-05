# Business search configuration
SEARCH_TERMS = [
    "restaurants"
]

# Target locations in Nairobi
LOCATIONS = [
    "Nairobi, Kenya",
    "Mombasa, Kenya",
    "Kisumu, Kenya",
    "Nakuru, Kenya",
    "Eldoret, Kenya",
    "Thika, Kenya",
    "Nyeri, Kenya",
    "Machakos, Kenya",
    "Malindi, Kenya",
    "Kitale, Kenya",
    "Garissa, Kenya",
    "Kakamega, Kenya",
    "Lamu, Kenya",
    "Naivasha, Kenya",
    "Voi, Kenya"
]

# Scraping parameters
MAX_RESULTS = 30
MIN_DELAY = 3.5
MAX_DELAY = 7.0
MAX_RETRIES = 3

# Output settings
OUTPUT_FILE = "nairobi_businesses.csv"
LOGS_DIR = "logs"

# Search radius (in kilometers)
RADIUS_KM = 30
# config.py (updated)
# ... existing configs ...
MIN_RATING = 3.5  # Minimum star rating
REQUIRE_NO_WEBSITE = True  # Only businesses without websites