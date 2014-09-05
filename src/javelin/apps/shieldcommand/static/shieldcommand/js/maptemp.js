/**
 * Created by adamshare on 9/5/14.
 */

var map;
var marker=[];
var image = new google.maps.MarkerImage('/images/blank.png',
    new google.maps.Size(100, 39),
    new google.maps.Point(0,0),
    new google.maps.Point(50, 39));
var bounds = new google.maps.LatLngBounds;
var infowindow = null;
var bounceTimer;
google.maps.visualRefresh = true;
var mapOptions = {
    zoomControl: false,
    mapTypeControl: false,
    streetViewControl: false,
	backgroundColor : "#ffffff",
//	scrollwheel : false,
	disableDoubleClickZoom : true
};
var mapStyles = [
    { stylers: [{ saturation: -100 }, { gamma: 1.5 }] },
    { elementType: "labels.text", stylers: [{ visibility: "off" }]},
    { featureType: "landscape", stylers: [{ visibility: "simplified" }] },
    { featureType: "transit", stylers: [{ visibility: "off" }] },
    { featureType: "poi", elementType: "labels.text", stylers: [{ visibility: "off" }] },
    { featureType: "poi", elementType: "labels.icon", stylers: [{ visibility: "off" }] },
    { featureType: "road", elementType: "geometry", stylers: [{ visibility: "simplified" }, { gamma: 1} ] },
    { featureType: "administrative.neighborhood", elementType: "labels.text.fill", stylers: [{ color: "#333333" }] },
    { featureType: "road.local", elementType: "labels.text", stylers: [{ weight: 0.5 }, { color: "#333333" }] },
    { featureType: "water", stylers: [{ visibility: "on" }, { saturation: 50 }, { gamma: 1}, { hue: "#50a5d1" }] }
];
var sites = [
	[
	'Rancho Bernardo',
	33.020899,
	-117.076526,
	1,
	'<div id="content"><h6>Rancho Bernardo</h6><div>11828 Bernardo Plaza Ct.<br />San Diego, CA - 92128<br /></div></div>',
	'RanchoBernardo',
	'SolanaBeachMarker'
	],[
	'Solana Beach',
	32.991981,
	-117.270562,
	2,
	'<div id="content"><h6>Solana Beach</h6><div>100 South Cedros Ave.<br />San Diego, CA - 92075<br /></div></div>',
	'SolanaBeach',
	'SolanaBeachMarker'
	]
];

// Define the overlay, derived from google.maps.OverlayView
    function Label(opt_options) {
         // Initialization
         this.setValues(opt_options);

         // Here go the label styles
         var div = this.div_ = document.createElement('div');
         div.className = 'maps-label-container';

         var span = this.span_ = document.createElement('span');
         span.className = 'pin bounce';
         div.appendChild(span);

         var span = this.span_ = document.createElement('span');
         span.className = 'pulse';
         div.appendChild(span);

//         var span = this.span_ = document.createElement('span');
//         span.className = 'maps-label';
//         span.style.cssText = 'margin-left: -70%; padding-top: 20px; white-space: nowrap;';
//         div.appendChild(span);
    };

    Label.prototype = new google.maps.OverlayView;

    Label.prototype.onAdd = function() {
         var pane = this.getPanes().overlayImage;
         pane.appendChild(this.div_);

         // Ensures the label is redrawn if the text or position is changed.
//         var me = this;
//         this.listeners_ = [
//              google.maps.event.addListener(this, 'position_changed',
//                   function() { me.draw(); }),
//              google.maps.event.addListener(this, 'text_changed',
//                   function() { me.draw(); }),
//              google.maps.event.addListener(this, 'zindex_changed',
//                   function() { me.draw(); })
//         ];
    };

    // Implement onRemove
    Label.prototype.onRemove = function() {
         this.div_.parentNode.removeChild(this.div_);

         // Label is removed from the map, stop updating its position/text.
         for (var i = 0, I = this.listeners_.length; i < I; ++i) {
              google.maps.event.removeListener(this.listeners_[i]);
         }
    };

    // Implement draw
    Label.prototype.draw = function() {
         var projection = this.getProjection();
         var position = projection.fromLatLngToDivPixel(this.get('position'));
         var div = this.div_;
         div.style.left = position.x + 'px';
         div.style.top = position.y + 'px';
         div.style.display = 'block';
         div.style.zIndex = this.get('zIndex'); //ALLOW LABEL TO OVERLAY MARKER
         this.span_.innerHTML = this.get('text').toString();
    };

jQuery('#footer').waypoint(function() {

    map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

    map.setOptions({styles: mapStyles});

    setMarkers(map, sites);

    infowindow = new google.maps.InfoWindow({content: "loading..."});

    //Instantiate Map
    function setMarkers(map, markers) {

    for (var i = 0; i < markers.length; i++) {
            var sites = markers[i];
            var siteLatLng = new google.maps.LatLng(sites[1], sites[2]);

			// Zoom to bounds
            bounds.extend(new google.maps.LatLng(sites[1], sites[2]));
			map.fitBounds(bounds);

			var marker = new google.maps.Marker({
                position: siteLatLng,
                map: map,
                icon: image,
                title: sites[0],
				optimized: false,
				draggable: false,
				animation: google.maps.Animation.DROP,
                html: sites[4]
            });

            var label = new Label({
                map: map
            });
            label.set('zIndex', 1234);
            label.bindTo('position', marker, 'position');
            label.set('text', sites[0]);

			// InfoWindows
            google.maps.event.addListener(marker, "click", function () {
                infowindow.setContent(this.html);
                infowindow.open(map, this);
            });

			// InfoWindows
            google.maps.event.addListener(label, "click", function () {
                infowindow.setContent(marker.html);
                infowindow.open(map, marker);
            });

			google.maps.event.addListener(map, "click", function() {
				infowindow.close();
			});


 			var mapDiv = document.getElementById(sites[5]);

			(function(temp_marker) {
				google.maps.event.addDomListener(mapDiv, 'mouseover', function() {
					if (temp_marker.getAnimation() == null || typeof temp_marker.getAnimation() === 'undefined') {
						temp_marker.setAnimation(google.maps.Animation.BOUNCE);
					}
				});

				google.maps.event.addDomListener(mapDiv, 'mouseout', function() {
					temp_marker.setAnimation(null);
				});

			}(marker));

        }
    }

}, { offset: '100%' });