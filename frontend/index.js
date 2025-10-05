let map;
let marker;
let infoWindow;
// let center = { lat: 40.749933, lng: -73.98633 }; // New York City
let latlong = {
  lat: 40.749933,
  lng: -73.98633
};
let range = {
  start: "2025-10-01",
  end: "2025-10-07"
};

async function initMap() {
    // Request needed libraries.
    //@ts-ignore
    const [{ Map }, { AdvancedMarkerElement }] = await Promise.all([
        google.maps.importLibrary("marker"),
        google.maps.importLibrary("places")
    ]);
  
    // Initialize the map.
    map = new google.maps.Map(document.getElementById('map'), {
        center: new google.maps.LatLng(40.749933, -73.98633),
        zoom: 5,
        mapId: '4504f8b37365c3d0',
        mapTypeControl: false,
    });
    // //@ts-ignore
    // const placeAutocomplete = new google.maps.places.PlaceAutocompleteElement();
    // //@ts-ignore
    // placeAutocomplete.id = 'place-autocomplete-input';
    // placeAutocomplete.locationBias = center;
    // const card = document.getElementById('place-autocomplete-card');
    // //@ts-ignore
    // card.appendChild(placeAutocomplete);
    // map.controls[google.maps.ControlPosition.TOP_LEFT].push(card);
    // // Create the marker and infowindow.
    // marker = new google.maps.marker.AdvancedMarkerElement({
    //     map,
    // });
    // infoWindow = new google.maps.InfoWindow({});
    // // Add the gmp-placeselect listener, and display the results on the map.
    // //@ts-ignore
    // placeAutocomplete.addEventListener('gmp-select', async ({ placePrediction }) => {
    //     const place = placePrediction.toPlace();
    //     await place.fetchFields({ fields: ['displayName', 'formattedAddress', 'location'] });
    //     // If the place has a geometry, then present it on a map.
    //     if (place.viewport) {
    //         map.fitBounds(place.viewport);
    //     }
    //     else {
    //         map.setCenter(place.location);
    //         map.setZoom(17);
    //     }
    //     let content = '<div id="infowindow-content">' +
    //         '<span id="place-displayname" class="title">' + place.displayName + '</span><br />' +
    //         '<span id="place-address">' + place.formattedAddress + '</span>' +
    //         '</div>';
    //   updateInfoWindow(content, place.location);
    //     marker.position = place.location;
    // });

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

        // Initialize autocomplete
        autocomplete = new google.maps.places.Autocomplete(input);

        // Optional: restrict to a country
        // autocomplete.setComponentRestrictions({ country: ["ca"] });

        // Listen for selection
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


  // Date range listener
  function initDateRangeListener() {
    const startDateInput = document.getElementById("start-date");
    const endDateInput = document.getElementById("end-date");
    const applyButton = document.getElementById("apply-date-range");

    // Set default dates (e.g., today and 7 days from now)
    const today = new Date();
    const nextWeek = new Date(today);
    nextWeek.setDate(today.getDate() + 7);

    startDateInput.valueAsDate = today;
    endDateInput.valueAsDate = nextWeek;

    // Apply button click handler
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

      // TODO: Fetch weather data for the selected date range
      // You can add your API call here
    });
  }

  initAutocomplete();
  initDateRangeListener();
}
// Helper function to create an info window.
function updateInfoWindow(content, center) {
    infoWindow.setContent(content);
    infoWindow.setPosition(center);
    infoWindow.open({
        map,
        anchor: marker,
        shouldFocus: false,
    });
}

// Search button click handler
window.onSearchClick = async function() {
  console.log("Search button clicked");
  console.log("Current location:", latlong);
  console.log("Current date range:", range);

  // Validate that location is set
  if (!latlong.lat || !latlong.lng) {
    alert("Please select a location first");
    return;
  }

  // Validate that date range is set
  if (!range.start || !range.end) {
    alert("Please select a date range first");
    return;
  }

  try {
    // Construct the API endpoint URL
    const apiUrl = `http://localhost:8000/weather`;
    
    // Prepare query parameters
    const params = {
      lat: latlong.lat,
      lng: latlong.lng,
      start_date: range.start,
      end_date: range.end
    };

    console.log("Sending GET request to:", apiUrl);
    console.log("With parameters:", params);

    // Make the GET request using axios
    const response = await axios.get(apiUrl, { params });

    console.log("Response received:", response.data);
    
    // TODO: Process and display the weather data
    alert("Weather data received! Check console for details.");

  } catch (error) {
    console.error("Error fetching weather data:", error);
    
    if (error.response) {
      // Server responded with error status
      alert(`Error: ${error.response.status} - ${error.response.data.message || 'Server error'}`);
    } else if (error.request) {
      // Request was made but no response received
      alert("Error: No response from server. Make sure the backend is running.");
    } else {
      // Something else happened
      alert(`Error: ${error.message}`);
    }
  }
};

initMap();