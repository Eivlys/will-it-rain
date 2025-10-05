import requests
import json
import os

# Create raw_data folder if it doesn't exist
os.makedirs('../raw_data', exist_ok=True)

print("Fetching predicted data from Meteomatics...")

try:
    response = requests.post('http://localhost:3001/api/forecast', 
        headers={'Content-Type': 'application/json'},
        json={
            'latitude': 43.46,
            'longitude': -80.52,
            'startDate': '2025-10-05T00:00:00Z',
            'endDate': '2025-10-12T23:00:00Z'
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        
        # Write to raw_data folder
        with open('../raw_data/waterloo_predicted.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        forecast_count = len(data.get('forecast', []))
        print(f"Created raw_data/waterloo_predicted.json with {forecast_count} records")
    else:
        print(f"Error: Status code {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("ERROR: Could not connect to http://localhost:3001")
    print("Make sure your Express server is running")
except Exception as e:
    print(f"Error: {e}")