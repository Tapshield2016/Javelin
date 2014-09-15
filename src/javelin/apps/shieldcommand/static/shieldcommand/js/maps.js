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
var spotCrimes = [];
var infoWindow = null;
var markerZIndex = 1;
var animatedOverlay;
var markerCluster;

function initializeMap() {
    var map_canvas = document.getElementById('map-canvas');

    googleMap = new google.maps.Map(map_canvas, googleMapOptions);

	markerOptions = {
		map: googleMap,
		animation: google.maps.Animation.DROP
//        optimized: false
	};

    //Accuracy bubble
	googleAccuracyCircleOptions = {
		strokeColor: '#41c4f2',
		strokeOpacity: 0.8,
		strokeWeight: 2,
		fillColor: '#41c4f2',
		fillOpacity: 0.35,
		map: googleMap
	};

    //If the agency uses the new "Region" model draw all regions
    //Else draw old single boundaries polygon
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
        geofence = new google.maps.Polygon({
            paths: googleMapAgencyBoundaries,
            strokeColor: '#0ab60a',
            strokeOpacity: 0.9,
            strokeWeight: 2,
            fillColor: '#76b676',
            fillOpacity: 0.15
        });

        geofence.setMap(googleMap);
    };

//         'styles': (object) An object that has style properties:
//         'url': (string) The image url.
//         'height': (number) The image height.
//         'width': (number) The image width.
//         'anchor': (Array) The anchor position of the label text.
//         'textColor': (string) The text color.
//         'textSize': (number) The text size.
//         'backgroundPosition': (string) The position of the backgound x, y.

    var x = 5;
    var y = 0;
    var style = [{
        url: '/media/static/shieldcommand/img/spotcrime/'+'pins_cluster_red.png',
        height: 40+x,
        width: 30,
        anchor: [x,y],
        textColor: '#d2322d',
        textSize: 10
    }];

    var mcOptions = {gridSize: 50, maxZoom: 13, zoomOnClick: true, styles:style};
    markerCluster = new MarkerClusterer(googleMap, [], mcOptions);
}

function setMapCenterToDefault() {
    googleMap.setCenter(googleMapOptions.center);
    googleMap.setZoom(googleMapOptions.zoom);
}

function clearActiveAlertMarker() {
    googleMapMarker.setMap(null);
    googleMapAccuracyCircle.setMap(null);

    if (animatedOverlay) {
        animatedOverlay.setMap(null);
        animatedOverlay = null;
    }
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

// Define the animated overlay, derived from google.maps.OverlayView
    function PinAnimation(opt_options) {
        this.setValues(opt_options);
        var div = this.div_ = document.createElement('div');
        div.id = 'holder';

        var span = this.span_ = document.createElement('span');
        span.className = 'pulse';
        div.appendChild(span);
    };

    PinAnimation.prototype = new google.maps.OverlayView;

    PinAnimation.prototype.onAdd = function() {
         var pane = this.getPanes().overlayShadow;
         pane.appendChild(this.div_);

         // Ensures the PinAnimation is redrawn if the text or position is changed.
         var me = this;
         this.listeners_ = [
              google.maps.event.addListener(this, 'position_changed',
                   function() { me.draw(); }),
         ];
    };

    // Implement onRemove
    PinAnimation.prototype.onRemove = function() {
         this.div_.parentNode.removeChild(this.div_);

         // PinAnimation is removed from the map, stop updating its position/text.
         for (var i = 0, I = this.listeners_.length; i < I; ++i) {
              google.maps.event.removeListener(this.listeners_[i]);
         }
    };

    // Set the visibility to 'hidden' or 'visible'.
    PinAnimation.prototype.hide = function() {
        if (this.div_) {
            this.div_.style.visibility = 'hidden';
        }
    };
    PinAnimation.prototype.show = function() {
        if (this.div_) {
            this.div_.style.visibility = 'visible';
        }
    };

    PinAnimation.prototype.colorForType = function(alertType) {

        var color;

        if (alertType == "emergency") {
            color ='#d2322d';
        }
        else if (alertType == "chat") {
            color ='orange';
        }
        else if (alertType == "timer") {
            color ='yellow';
        }
        else if (alertType == "static") {
            color ='#5bc0de';
        }

        if (this.div_) {
            this.span_.style.border = '10px solid '+ color;
        }

        //Accuracy bubble color change
	    googleAccuracyCircleOptions = {
	    	strokeColor: color,
	    	strokeOpacity: 0.6,
	    	strokeWeight: 2,
	    	fillColor: color,
	    	fillOpacity: 0.25,
	    	map: googleMap
	    };
    };

    // Implement draw
    PinAnimation.prototype.draw = function() {
        var topPadding = 0;
        var sizeHeight = 50
        var sizeWidth = sizeHeight;
        var centerX = sizeWidth/2;
        var centerY = sizeHeight/2;

         var projection = this.getProjection();
         var position = projection.fromLatLngToDivPixel(this.get('position'));
         var div = this.div_;
        //Adjust overlay position to be centered over the point
         div.style.left = position.x-centerX + 'px';
         div.style.top = position.y-topPadding-centerY + 'px';
         div.style.display = 'block';
    };

function updateMarker(location) {
    if (!location) {
        return;
    }

    alert_location = new google.maps.LatLng(location.latitude, location.longitude);

    googleMapMarker.setPosition(alert_location);
    googleMapMarker.setTitle(location.title);
    googleMapMarker.setIcon(getIconForLocation(location));
	bringMarkerToFront(googleMapMarker);
	
	if (location.accuracy) {
    	googleMapAccuracyCircle.setCenter(alert_location);
    	googleMapAccuracyCircle.setRadius(location.accuracy);
	}

    var currentBounds = googleMap.getBounds()
    if (!currentBounds.contains(alert_location)) {
        googleMap.setCenter(googleMapMarker.getPosition());
    }
}

//Sets correct icon for alert, spotcrime, or social crime reports
function getIconForLocation(location) {
	var icon = 'NewUserPin.png';
	
    if (location)
	{
		if (location.type == 'alert')
		{
        	icon = location.alertType ? location.alertType.charAt(0).toUpperCase() + location.alertType.substr(1).toLowerCase() + 'UserPin.png' : icon;

//            if (location.alertType == "static") {
//                return '/media/static/shieldcommand/img/userpin/' + icon;
//            }
//            var image = {
//                url: '/media/static/shieldcommand/img/userpin/' + icon,
//                size: new google.maps.Size(28, 50),
//                origin: new google.maps.Point(0,0),
//                anchor: new google.maps.Point(14, 25)
//            };
//		    return image;
        }
		else if (location.type == 'crimeTip' || location.type == 'spotCrime')
		{
			var crimeType = location.reportType ? location.reportType.toLowerCase().replace(/[\s\/]/g, '') : 'other';
			
			icon = location.type.toLowerCase() + '/' + 'pins_' + crimeType + '_icon.png';
		}
    }
    
	return '/media/static/shieldcommand/img/' + icon;
}

//Set marker for active alert or crime tip
function setMarker(location) {
    if (!location) {
        return;
    };
    closeInfoWindow();
    googleMapMarker.setOptions(markerOptions);
    var alert_location = new google.maps.LatLng(location.latitude, location.longitude);
    googleMapMarker.setPosition(alert_location);
    googleMapMarker.setIcon(getIconForLocation(location));
    googleMapMarker.setTitle(location.title);
    googleMapMarker.setMap(googleMap);
	bringMarkerToFront(googleMapMarker);

    if (location.type == 'alert') {

        if (!animatedOverlay) {
            animatedOverlay = new PinAnimation({
                map: googleMap
            });
        }
        animatedOverlay.bindTo('position', googleMapMarker, 'position');
        animatedOverlay.show();

        animatedOverlay.colorForType(location.alertType)
    }
	
	if (location.accuracy)
	{
    	googleMapAccuracyCircle.setOptions(googleAccuracyCircleOptions);
		googleMapAccuracyCircle.setCenter(alert_location);
    	googleMapAccuracyCircle.setRadius(location.accuracy);
	}
    else if (location.type == 'alert') {
        googleMapAccuracyCircle.setMap(null);
    }
	
    googleMap.setZoom(17);
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

	googleMap.setZoom(17);
	
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

        if (crime.showPin || crime.type == 'spotCrime') {

            map = googleMap;
        }

		var marker = new google.maps.Marker({
			position: new google.maps.LatLng(crime.latitude, crime.longitude),
			map: map,
			title: crime.title,
			icon: getIconForLocation(crime),
			animation: google.maps.Animation.DROP
        });

		if ( ! crimeMarkers[crime.type])
		{
			crimeMarkers[crime.type] = [];
		}

		crimeMarkers[crime.type][crime.object_id] = marker;

		if (crime.type == 'crimeTip')
		{
			google.maps.event.addListener(marker, 'click', crimeTipPinClicked);
		}
		else if (crime.type == 'spotCrime')
		{

			spotCrimes[crime.object_id] = crime;
			google.maps.event.addListener(marker, 'click', spotCrimePinClicked);

            markerCluster.addMarker(marker);

//            google.maps.event.addListener(marker, 'mouseover', spotCrimePinClicked);
//            google.maps.event.addListener(marker, 'mouseout', closeInfoWindow);
		}
	}
}

function crimeTipPinClicked(evt)
{
	closeInfoWindow();
	
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
				
				break;
			}
		}
	}
}

function spotCrimePinClicked(evt)
{
	if (crimeMarkers['spotCrime'])
	{
		for (spotCrimeID in crimeMarkers['spotCrime'])
		{
			var marker = crimeMarkers['spotCrime'][spotCrimeID];
			
			if (marker.getPosition() == evt.latLng)
			{
				var spotCrime = spotCrimes[spotCrimeID];
                closeInfoWindow();
//				zoomToCrime(spotCrime);
				var date = new Date();
				date.setTime(Date.parse(spotCrime.creationDate));
				console.log(date.toISOString());
				var titleID = 'sc-title-' + spotCrimeID;
				var contentID = 'sc-content-' + spotCrimeID;
				var infoContent = '<h4 style="margin-top: 0">' + marker.title + '</h4>' +
				'<div id="' + contentID + '">' +
				'<table class="table table-condensed">' +
				'<tr><td><strong>Date</td><td>' + date.toLocaleDateString() + " " + date.toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit'}) + '</td></tr>' +
				'<tr><td><strong>Address</td><td>' + spotCrime.address + '</td></tr>' +
				'</table>' +
				'<p style="margin-top: 10px"><a class="btn btn-info" href="' + spotCrime.link + '" target="_blank">More Info</a></p>' +
				'</div>';
				
				infoWindow = new google.maps.InfoWindow({
					content: infoContent
				});
				
				infoWindow.open(googleMap, marker);
				
				/*Javelin.getSpotCrime(spotCrimeID, function(spotCrime) {
					if ( ! spotCrime)
					{
						return;
					}
					
					$('#' + titleID).html(spotCrime.title);
					var date = new Date(attributes.date);
					$('#' + contentID).html('<table>' +
					'<tr><td><strong>Date</td><td>' + date.toISOString().slice(0, 10) + '</td></tr>' +
					'<tr><td><strong>Address</td><td>' + spotCrime.address + '</td></tr>' +
					'<tr><td><strong>Description</td><td>' + spotCrime.description + '</td></tr>' +
					'</table>' +
					'<p><a class="btn btn-info" href="' + spotCrime.link + '" target="_blank">More Info</a></p>');
				});*/
				
				break;
			}
		}
	}
}

function closeInfoWindow()
{
	if ( ! infoWindow)
	{
		return;
	}
	
	infoWindow.close();
}

function showCrimeMarker(crime) {

    if ( ! crime) {
        return;
    }

	closeInfoWindow();

	if (crimeMarkers[crime.type][crime.object_id].map == googleMap) {
		return;
	}

	if (crimeMarkers[crime.type] && crimeMarkers[crime.type][crime.object_id]) {
		crimeMarkers[crime.type][crime.object_id].setMap(googleMap);
	}
}

function showCrimeMarkers(crimes) {

    if ( ! crimes) {
        return;
    }
	
	for (var i = 0; i < crimes.length; i++)
	{
		showCrimeMarker(crimes[i]);
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

        if (!crime) {
			continue;
		}

        if (crime.showPin) {
            crime.showPin = false;
        }

		if (crimeMarkers[crime.type] && crimeMarkers[crime.type][crime.object_id])
		{
			crimeMarkers[crime.type][crime.object_id].setMap(null);
		}
	}
}