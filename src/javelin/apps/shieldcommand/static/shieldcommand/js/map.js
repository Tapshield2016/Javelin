var googleMap;
var googleMapOptions = {};
var googleMarkerOptions = {};
var googleAccuracyCircleOptions = {};
var googleMapMarker = new google.maps.Marker();
var googleMapAccuracyCircle = new google.maps.Circle();
var googleMapGeocoder = new google.maps.Geocoder();
var googleMapAgencyBoundaries = [];
var googleMapRegions = [];
var crimeMarkers = [];
var markerZIndex = 1;

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

    if (googleMapRegions.length > 0) {

        geofence = new google.maps.Polygon({
                paths: googleMapRegions,
                strokeColor: '#0ab60a',
                strokeOpacity: 0.9,
                strokeWeight: 2,
                fillColor: '#76b676',
                fillOpacity: 0.15
        });

        geofence.setMap(googleMap);
    }
    else if (googleMapAgencyBoundaries.length > 0) {
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

function updateMarker(location) {
    if (!location) {
        return;
    }
    alert_location = new google.maps.LatLng(location.latitude, location.longitude);
    googleMapMarker.setPosition(alert_location);
    googleMapMarker.setTitle(location.title);
    googleMapMarker.setIcon(getIconForLocation(location));
	bringMarkerToFront(googleMapMarker);
	
	if (location.accuracy)
	{
    	googleMapAccuracyCircle.setCenter(alert_location);
    	googleMapAccuracyCircle.setRadius(location.accuracy);
	}
}

function getIconForLocation(location) {
	var icon = 'NewUserPin.png';
	
    if (location)
	{
		if (location.type == 'alert')
		{
        	icon = location.alertStatus != 'N' && location.alertType ? location.alertType.charAt(0).toUpperCase() + location.alertType.substr(1).toLowerCase() + 'UserPin.png' : icon; 
		}
		else if (location.type == 'crimeTip' || location.type == 'spotCrime')
		{
			var crimeType = location.reportType ? location.reportType.toLowerCase().replace(/[\s\/]/g, '') : 'other';
			
			icon = location.type.toLowerCase() + '/' + 'pins_' + crimeType + '_icon.png';
		}
    }
    
	return '/media/static/shieldcommand/img/' + icon;
}

function setMarker(location) {
    if (!location) {
        return;
    };
    googleMapMarker.setOptions(markerOptions);
    var alert_location = new google.maps.LatLng(location.latitude, location.longitude);
    googleMapMarker.setPosition(alert_location);
    googleMapMarker.setIcon(getIconForLocation(location));
    googleMapMarker.setTitle(location.title);
    googleMapMarker.setMap(googleMap);
	bringMarkerToFront(googleMapMarker);
	
	if (location.accuracy)
	{
    	googleMapAccuracyCircle.setOptions(circleOptions);
		googleMapAccuracyCircle.setCenter(alert_location);
    	googleMapAccuracyCircle.setRadius(location.accuracy);
	}
	
    googleMap.setZoom(18);
    googleMap.setCenter(googleMapMarker.getPosition());
}

function bringMarkerToFront(marker)
{
	marker.setZIndex(google.maps.Marker.MAX_ZINDEX + markerZIndex);
	markerZIndex++;
}

function zoomToCrime(crime)
{
	if (! crime)
	{
		return;
	}
	
	googleMap.setZoom(18);
	
	if (crimeMarkers[crime.type] && crimeMarkers[crime.type][crime.object_id])
	{
		clearActiveAlertMarker();
		bringMarkerToFront(crimeMarkers[crime.type][crime.object_id]);
	}
	
	var crimeLocation = new google.maps.LatLng(crime.latitude, crime.longitude);   
    googleMap.setCenter(crimeLocation);
}

function addCrimeMarkers(crimes) {
    if (! crimes)
	{
		return;
	}
	
	for (var i = 0; i < crimes.length; i++)
	{
		var crime = crimes[i];
		
		if ( ! crime || (crimeMarkers[crime.type] && crimeMarkers[crime.type][crime.object_id]))
		{
			continue;
		}

        var map = null;

        if (crime.showPin) {

            map = googleMap;
        }
		
		var marker = new google.maps.Marker({
			position: new google.maps.LatLng(crime.latitude, crime.longitude),
			map: map,
			title: crime.reportType,
			icon: getIconForLocation(crime)
        });
        marker.setAnimation(google.maps.Animation.DROP);
		
		if ( ! crimeMarkers[crime.type])
		{
			crimeMarkers[crime.type] = [];
		}
		
		//marker.crimeType = crime.type;
		//marker.crimeId = crime.object_id;
		crimeMarkers[crime.type][crime.object_id] = marker;
		
		google.maps.event.addListener(marker, 'click', crimePinClicked);
	}
}

function crimePinClicked(evt)
{
	if (crimeMarkers['crimeTip'])
	{
		for (crimeTipID in crimeMarkers['crimeTip'])
		{
			var marker = crimeMarkers['crimeTip'][crimeTipID];
			
			if (marker.getPosition() == evt.latLng)
			{
				var scrollContainer = $('#crimeTipList');
				
				if ( ! scrollContainer.is(':visible'))
				{
					$('#crimeTipListLink').click();
				}
				
				var crimeTipItem = $('#crimeTip-' + crimeTipID);
				crimeTipItem.click();
				scrollContainer.animate({
				    scrollTop: crimeTipItem.offset().top - scrollContainer.offset().top + scrollContainer.scrollTop()
				});
			}
		}
	}
}

function showCrimeMarker(crime) {

    if (!crime) {
        return;
    }

    if (crimeMarkers[crime.type][crime.object_id].map == googleMap) {
        return;
    }

    if (crimeMarkers[crime.type] && crimeMarkers[crime.type][crime.object_id]) {
        crimeMarkers[crime.type][crime.object_id].setMap(googleMap);
        crimeMarkers[crime.type][crime.object_id].setAnimation(google.maps.Animation.DROP);
    }
}

function hideCrimeMarkers(crimes)
{
	if ( ! crimes)
	{
		return;
	}
	
	for (var i = 0; i < crimes.length; i++)
	{
		var crime = crimes[i];

        if (crime.showPin) {
            crime.showPin = false;
        }
		
		if ( ! crime)
		{
			continue;
		}
		
		if (crimeMarkers[crime.type] && crimeMarkers[crime.type][crime.object_id])
		{
			crimeMarkers[crime.type][crime.object_id].setMap(null);
		}
	}
}