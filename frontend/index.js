let map;
let marker;
let infoWindow;
let latlong = {
  lat: 40.749933,
  lng: -73.98633
};
let range = {
  start: "2025-10-01",
  end: "2025-10-07"
};

async function initMap() {
    const [{ Map }, { AdvancedMarkerElement }] = await Promise.all([
        google.maps.importLibrary("marker"),
        google.maps.importLibrary("places")
    ]);
  
    map = new google.maps.Map(document.getElementById('map'), {
        center: new google.maps.LatLng(40.749933, -73.98633),
        zoom: 5,
        mapId: '4504f8b37365c3d0',
        mapTypeControl: false,
    });

    var getTileUrl = function (tile, zoom) {
        return '//gibs.earthdata.nasa.gov/wmts/epsg3857/best/' +
          'MODIS_Terra_Aerosol/default/2013-12-02/' +
          'GoogleMapsCompatible_Level6/' +
          zoom + '/' + tile.y + '/' +
          tile.x + '.png';
      };

      var layerOptions = {
        alt: 'MODIS_Terra_Aerosol',
        getTileUrl: getTileUrl,
        maxZoom: 6,
        minZoom: 1,
        name: 'MODIS_Terra_Aerosol',
        tileSize: new google.maps.Size(256, 256),
        opacity: 0.5
      };

      var imageMapType = new google.maps.ImageMapType(layerOptions);
  map.overlayMapTypes.insertAt(0, imageMapType);
  
  let autocomplete;

  function initAutocomplete() {
        const input = document.getElementById("autocomplete");
        autocomplete = new google.maps.places.Autocomplete(input);

        autocomplete.addListener("place_changed", () => {
          const place = autocomplete.getPlace();
          console.log(place);

          if (!place.geometry || !place.geometry.location) {
            alert("No location data available for this place");
            return;
          }

          latlong.lat = place.geometry.location.lat();
          latlong.lng = place.geometry.location.lng();

          console.log("Latitude:", latlong.lat);
          console.log("Longitude:", latlong.lng);

          document.getElementById("lat").textContent = latlong.lat.toFixed(6);
          document.getElementById("lng").textContent = latlong.lng.toFixed(6);
        });
  }

  function initDateRangeListener() {
    const startDateInput = document.getElementById("start-date");
    const endDateInput = document.getElementById("end-date");
    const applyButton = document.getElementById("apply-date-range");

    const today = new Date();
    const nextWeek = new Date(today);
    nextWeek.setDate(today.getDate() + 7);

    startDateInput.valueAsDate = today;
    endDateInput.valueAsDate = nextWeek;

    applyButton.addEventListener("click", () => {
      const startDate = startDateInput.value;
      const endDate = endDateInput.value;

      if (!startDate || !endDate) {
        alert("Please select both start and end dates");
        return;
      }

      if (new Date(startDate) > new Date(endDate)) {
        alert("Start date must be before end date");
        return;
      }

      const startDateObj = new Date(startDate);
      const endDateObj = new Date(endDate);

      console.log("Date Range Selected:");
      console.log("Start Date:", startDateObj.toISOString());
      console.log("End Date:", endDateObj.toISOString());

      range.start = startDateObj.toISOString();
      range.end = endDateObj.toISOString();
    });
  }

  initAutocomplete();
  initDateRangeListener();
}

function updateInfoWindow(content, center) {
    infoWindow.setContent(content);
    infoWindow.setPosition(center);
    infoWindow.open({
        map,
        anchor: marker,
        shouldFocus: false,
    });
}

window.onSearchClick = async function() {
  console.log("Search button clicked");
  console.log("Current location:", latlong);
  console.log("Current date range:", range);

  if (!latlong.lat || !latlong.lng) {
    alert("Please select a location first");
    return;
  }

  if (!range.start || !range.end) {
    alert("Please select a date range first");
    return;
  }

  try {
    const apiUrl = `http://localhost:8000/predict`;
    const requestBody = {
      latitude: latlong.lat,
      longitude: latlong.lng,
      target_time: range.start,
      end_time: range.end
    };
    console.log("Sending POST request to:", apiUrl);
    console.log("With body:", requestBody);

    const response = await axios.post(apiUrl, requestBody);
    console.log("Response received:", response.data);

    const container = document.getElementById('predictions-container');
    const list = document.getElementById('predictions-list');

    if (response.data && response.data.predictions) {
      list.innerHTML = '';
    
      response.data.predictions.forEach(pred => {
        const predDiv = document.createElement('div');
        predDiv.style.cssText = 'margin: 8px 0; padding: 15px; background: rgba(0, 0, 0, 0.75); border-radius: 8px; color: white; border-left: 4px solid #4CAF50;';
    
        const predictedPrecip = pred.predicted_precip_mm || pred.precipitation_mm || 0;
        const historicalAvg = pred.historical_avg_precip_mm || 0;
        const diff = pred.difference_from_avg || 0;
    
        let weatherDescription;
if (predictedPrecip < 0.1) {
  weatherDescription = 'Clear skies expected';
} else {
  // Get the intensity and type from backend
  const confidence = pred.confidence_percent || 0;
  const type = pred.type || 'precipitation';
  const intensity = pred.intensity || '';
  
  // Add historical comparison
  let comparison = '';
  if (diff > 0.5) {
    comparison = ' - wetter than usual';
  } else if (diff < -0.5) {
    comparison = ' - drier than usual';
  } else {
    comparison = ' - typical';
  }
  
  weatherDescription = `${confidence}% chance of ${intensity} ${type}${comparison}`;
}
    
        predDiv.innerHTML = `
          <div style="font-size: 16px; font-weight: bold; margin-bottom: 8px;">
            ${weatherDescription}
          </div>
          <div style="font-size: 14px; color: #ddd;">
            Predicted: ${predictedPrecip.toFixed(1)}mm | 
            5-yr avg: ${historicalAvg.toFixed(1)}mm | 
            Temp: ${pred.temperature_c?.toFixed(1) || 'N/A'}°C
          </div>
          <div style="font-size: 12px; color: #aaa; margin-top: 5px;">
            ${new Date(pred.timestamp).toLocaleString()}
          </div>
        `;
        list.appendChild(predDiv);
      });
    
      container.style.display = 'block';
    }
  } catch (error) {
    console.error("Error fetching weather data:", error);
    
    if (error.response) {
      alert(`Error: ${error.response.status} - ${error.response.data.message || 'Server error'}`);
    } else if (error.request) {
      alert("Error: No response from server. Make sure the backend is running.");
    } else {
      alert(`Error: ${error.message}`);
    }
  }
};

window.initMap = initMap;