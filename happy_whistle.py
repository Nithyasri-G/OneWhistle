import requests
import json
import random
import os
import winsound
import threading
import time

# --- CONFIGURATION ---

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyArIJ_2WRGI7nOzfzmXSZXs5HXaCPxLnWE')
OFFERS = [
    "Buy 1 Get 1 on Cocktails",
    "50% off on Beer", 
    "Free Dessert with Meal",
    "Flat 20% Off on Dinner",
    "Unlimited Mocktails for 2 Hours",
    "Happy Hour Wings Special",
    "2-for-1 Wine by the Glass",
    "Half Price Appetizers",
    "Free Wine with Dinner",
    "30% off Pizza and Pasta"
]

# --- WHISTLE SOUND GENERATOR ---
class WhistleSound:
    @staticmethod
    def play_whistle():
        """Play realistic whistle sound on Windows"""
        try:
            # Create a whistle-like sound sequence
            # Referee whistle pattern: high-low-high with varying durations
            whistle_sequence = [
                (2800, 400),  # High pitch, longer duration
                (2400, 200),  # Mid pitch, short
                (3200, 300),  # Higher pitch, medium
                (2600, 250),  # Mid-high pitch
                (3000, 500),  # High pitch, long finish
            ]
            
            for frequency, duration in whistle_sequence:
                winsound.Beep(frequency, duration)
                time.sleep(0.05)  # Short pause between tones
                
        except Exception as e:
            print(f"Could not play whistle sound: {e}")
            # Fallback to simple beeps
            for _ in range(3):
                winsound.Beep(2500, 300)
                time.sleep(0.1)
    
    @staticmethod
    def play_celebration_whistle():
        """Play a celebratory whistle when multiple deals are found"""
        try:
            # Two quick whistles for celebration
            for _ in range(2):
                WhistleSound.play_whistle()
                time.sleep(0.3)
        except Exception as e:
            print(f"Could not play celebration whistle: {e}")

# --- RESTAURANT COLLECTOR ---
def collect_happy_hour_restaurants(location: dict, radius: int = 1000) -> list:
    """Collect restaurants with happy hour deals"""
    lat, lng = location["latitude"], location["longitude"]
    url = (
        "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={lat},{lng}&radius={radius}&type=restaurant&key={GOOGLE_API_KEY}"
    )
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "OK":
            return []
            
    except requests.exceptions.RequestException:
        return []
    
    results = []
    
    for place in data.get("results", []):
        # 50% chance this restaurant has a deal
        if random.random() < 0.5:
            deal = {
                "store_name": place.get("name"),
                "store_address": {
                    "lat": place["geometry"]["location"]["lat"],
                    "lng": place["geometry"]["location"]["lng"]
                },
                "offer_details": random.choice(OFFERS),
                "offer_validity_hours": random.randint(2, 5),
                "alert_radius_km": 1,
                "provider": True
            }
            results.append(deal)
    
    # Play whistle sound based on number of deals found
    if results:
        def play_sound():
            if len(results) >= 5:
                WhistleSound.play_celebration_whistle()
            else:
                WhistleSound.play_whistle()
        
        # Play sound in separate thread to avoid blocking
        threading.Thread(target=play_sound, daemon=True).start()
    
    return results

def main():
    """Main function that returns only the deals list in JSON format"""
    try:
        lat_input = input("Enter latitude: ").strip()
        lng_input = input("Enter longitude: ").strip()
        
        latitude = float(lat_input)
        longitude = float(lng_input)
        
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            print(json.dumps([]))
            return
            
        location = {"latitude": latitude, "longitude": longitude}
        deals = collect_happy_hour_restaurants(location)
        
        # Output the JSON result
        print(json.dumps(deals, indent=2))
        
        # Give some time for the whistle sound to play
        if deals:
            time.sleep(2)
        
    except (ValueError, EOFError):
        print(json.dumps([]))
    except Exception:
        print(json.dumps([]))

if __name__ == "__main__":
    main()