// Geolocation Tracking Functionality

let userLocation = null;

// Get user's current location
function getUserLocation() {
    const locationBtn = document.getElementById('get-location-btn');
    const locationInfo = document.getElementById('location-info');
    const locationText = document.getElementById('location-text');

    if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser.');
        return;
    }

    if (locationBtn) {
        locationBtn.disabled = true;
        locationBtn.textContent = 'Getting location...';
    }

    navigator.geolocation.getCurrentPosition(
        // Success callback
        async function (position) {
            console.log('Position acquired:', position);
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;

            userLocation = {
                latitude: latitude,
                longitude: longitude
            };

            // Set hidden input values
            if (document.getElementById('latitude-input')) document.getElementById('latitude-input').value = latitude;
            if (document.getElementById('longitude-input')) document.getElementById('longitude-input').value = longitude;

            // Updated UI Element Retrieval
            const locationStatus = document.getElementById('location-status');
            const locationSuccess = document.getElementById('location-success');
            const locationDisplay = document.getElementById('location-display');

            // IMMEDIATE FEEDBACK: Stop spinner and show coordinates
            if (locationStatus) locationStatus.style.display = 'none';
            if (locationSuccess) {
                locationSuccess.style.display = 'flex';
                locationSuccess.style.alignItems = 'center';
            }
            // Temporarily show coordinate feedback while geocoding
            if (locationDisplay) {
                locationDisplay.textContent = `Location captured: ${latitude.toFixed(4)}, ${longitude.toFixed(4)}`;
            }

            if (locationInfo) {
                locationInfo.style.display = 'block';
            }

            // Re-retrieve button to be safe
            const btn = document.getElementById('get-location-btn');
            if (btn) {
                btn.style.display = 'none';
            }

            // Trigger button state update
            if (typeof updateSubmitButton === 'function') {
                updateSubmitButton();
            }

            // Try to get city and country using reverse geocoding
            try {
                const locationDetails = await reverseGeocode(latitude, longitude);
                userLocation.city = locationDetails.city;
                userLocation.country = locationDetails.country;

                if (document.getElementById('city-input')) document.getElementById('city-input').value = locationDetails.city;
                if (document.getElementById('country-input')) document.getElementById('country-input').value = locationDetails.country;

                // Update display with resolved address
                if (locationDisplay) {
                    locationDisplay.textContent = `Location captured: ${locationDetails.city}, ${locationDetails.country}`;
                }

                // Legacy support for old location text element
                if (locationText) {
                    locationText.textContent = `${locationDetails.city}, ${locationDetails.country}`;
                }
            } catch (error) {
                console.error('Reverse geocoding failed:', error);
                // No need to change UI as coordinates are already shown
            }

            console.log('Location captured and processed:', userLocation);
        },
        // Error callback
        function (error) {
            console.error('Geolocation error details:', error);

            let errorMessage = 'Unable to get your location. ';
            switch (error.code) {
                case error.PERMISSION_DENIED:
                    errorMessage += 'Please allow location access in your browser settings.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMessage += 'Location information is unavailable.';
                    break;
                case error.TIMEOUT:
                    errorMessage += 'Location request timed out. Please try again.';
                    break;
                default:
                    errorMessage += 'An unknown error occurred (' + error.message + ').';
            }

            // On non-secure contexts (HTTP), geolocation might be blocked silently or fail.
            if (window.location.protocol !== 'https:' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
                errorMessage += ' (Geolocation requires HTTPS)';
            }

            // Update UI with error state
            const locationStatus = document.getElementById('location-status');
            const locationError = document.getElementById('location-error');

            if (locationStatus) locationStatus.style.display = 'none';
            if (locationError) locationError.style.display = 'block';

            alert(errorMessage);

            if (locationBtn) {
                locationBtn.disabled = false;
                locationBtn.textContent = 'Retry Location';
            }
        },
        // Options
        {
            enableHighAccuracy: false, // Set to false for faster response if high accuracy fails
            timeout: 15000,
            maximumAge: 0
        }
    );
}

// Reverse geocoding using OpenStreetMap Nominatim API
async function reverseGeocode(latitude, longitude) {
    try {
        const response = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=10`
        );

        if (!response.ok) {
            throw new Error('Geocoding API request failed');
        }

        const data = await response.json();

        return {
            city: data.address.city || data.address.town || data.address.village || 'Unknown',
            country: data.address.country || 'Unknown'
        };
    } catch (error) {
        console.error('Reverse geocoding error:', error);
        return {
            city: 'Unknown',
            country: 'Unknown'
        };
    }
}

// Auto-initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    const locationBtn = document.getElementById('get-location-btn');

    if (locationBtn) {
        locationBtn.addEventListener('click', getUserLocation);
    }

    // Auto-request location on voting page
    const autoGetLocation = document.getElementById('auto-get-location');
    if (autoGetLocation && autoGetLocation.value === 'true') {
        console.log('Auto-requesting location...');
        // Trigger immediately instead of delayed
        getUserLocation();
    }
});
