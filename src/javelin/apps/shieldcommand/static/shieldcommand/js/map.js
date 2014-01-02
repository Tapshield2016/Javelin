var googleMap;
var googleMapOptions = {};
var googleMarkerOptions = {};
var googleAccuracyCircleOptions = {};
var googleMapMarker = new google.maps.Marker();
var googleMapAccuracyCircle = new google.maps.Circle();
var googleMapGeocoder = new google.maps.Geocoder();
var googleMapAgencyBoundaries = [];

function initializeMap() {
    var map_canvas = document.getElementById('map-canvas');

    googleMap = new google.maps.Map(map_canvas, googleMapOptions);

	markerOptions = {
		map: googleMap,
		animation: google.maps.Animation.DROP
	};

	circleOptions = {
		strokeColor: '#41c4f2',
		strokeOpacity: 0.8,
		strokeWeight: 2,
		fillColor: '#41c4f2',
		fillOpacity: 0.35,
		map: googleMap
	};

    if (googleMapAgencyBoundaries.length > 0) {
        bermudaTriangle = new google.maps.Polygon({
            paths: googleMapAgencyBoundaries,
            strokeColor: '#0ab60a',
            strokeOpacity: 0.9,
            strokeWeight: 2,
            fillColor: '#76b676',
            fillOpacity: 0.15
        });

        bermudaTriangle.setMap(googleMap);        
    };
}

function setMapCenterToDefault() {
    googleMap.setCenter(googleMapOptions.center);
    googleMap.setZoom(googleMapOptions.zoom);
}

function clearActiveAlertMarker() {
    googleMapMarker.setMap(null);
    googleMapAccuracyCircle.setMap(null);
}

function addressForLocation(location, callback) {
    if (!location) {
        callback(null);
        return;
    };
    var latLong = new google.maps.LatLng(location.latitude, location.longitude);
    googleMapGeocoder.geocode({'location': latLong}, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            callback(results[0].formatted_address);
        }
    });
}

function setMarker(location) {
    if (!location) {
        return;
    };
    googleMapMarker.setOptions(markerOptions);
    googleMapAccuracyCircle.setOptions(circleOptions);
    alert_location = new google.maps.LatLng(location.latitude, location.longitude);
    googleMapMarker.setPosition(alert_location);
    googleMapMarker.setIcon('/media/static/shieldcommand/img/NewUserPin.png');
    googleMapAccuracyCircle.setCenter(alert_location);
    googleMapAccuracyCircle.setRadius(location.accuracy);
    googleMap.setZoom(18)
    googleMap.setCenter(googleMapMarker.getPosition())
}