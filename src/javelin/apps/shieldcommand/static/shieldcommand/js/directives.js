'use strict';

/* Directives */


angular.module('shieldCommand.directives', [])

.directive('appVersion', ['version', function(version) {
    return function(scope, elm, attrs) {
      elm.text(version);
    };
 }])

.directive('dismissMarkCompletedModal', function() {
   return {
     restrict: 'A',
     link: function(scope, element, attr) {
       scope.dismissMarkCompletedModal = function() {
           element.modal('hide');
          console.log(element);
       };
     }
   } 
})

.directive('dismissMarkPendingModal', function() {
   return {
     restrict: 'A',
     link: function(scope, element, attr) {
       scope.dismissMarkPendingModal = function() {
           element.modal('hide');
        console.log(element);
       };
     }
   } 
})

.directive('commandAlertModal', function() {
   return {
     restrict: 'A',
     link: function(scope, element, attr) {
       scope.dismiss = function() {
           element.modal('hide');
       };
     }
   } 
})

.directive('mapControls', ['$filter', '$rootScope', function($filter, $rootScope) {
  return {
    restrict: 'A',
    link: function(scope, element, attr) {
      scope.alertsNavMaximized = false;
      scope.allAlertsToggled = false;
      scope.tempMapMarkers = [];

      scope.toggleControls = function() {
        if (!scope.alertsNavMaximized) { 
          $('#alerts-nav ul').removeClass('minimized').addClass('maximized');
          $('#alerts-nav li.alert-toggle').removeClass('hide');
        }
        else {
          $('#alerts-nav ul').addClass('minimized').removeClass('maximized');
          $('#alerts-nav li.alert-toggle').addClass('hide');
        }
        scope.alertsNavMaximized = !scope.alertsNavMaximized;
      }

      scope.toggleSelectedAlerts = function(element) {
        if ($(element).hasClass('selected')) {
          $(element).removeClass('selected');
        }
        else {
          $(element).addClass('selected');
        }
        scope.setTempMarkers();
      }

      scope.toggleMyAlerts = function() {
        scope.toggleSelectedAlerts('#myAlerts-toggle');
      }

      scope.toggleNewAlerts = function() {
        scope.toggleSelectedAlerts('#newAlerts-toggle');
      }

      scope.togglePendingAlerts = function() {
        scope.toggleSelectedAlerts('#pendingAlerts-toggle');
      }

      scope.togglePastAlerts = function() {
        scope.toggleSelectedAlerts('#pastAlerts-toggle');
      }

      scope.toggleAllAlerts = function() {
        if (!scope.allAlertsToggled) {
          $('#alerts-nav li.alert-toggle').addClass('selected');   
          scope.setTempMarkers();       
        }
        else {
          $('#alerts-nav li.alert-toggle').removeClass('selected');
          scope.clearMarkers();
        }
        scope.allAlertsToggled = !scope.allAlertsToggled;
      }

      scope.clearMarkers = function() {
        for (var i = 0; i < scope.tempMapMarkers.length; i++) {
          scope.tempMapMarkers[i].setMap(null);
        };
        scope.tempMapMarkers = [];
      }

      scope.setTempMarkers = function() {
        scope.clearMarkers();
        var statuses = [];
        var locations = [];

        $('#alerts-nav li.alert-toggle').each(function () {
          if ($(this).hasClass('selected')) {
            if ($(this).attr('id') == 'myAlerts-toggle') {
              statuses.push('A');
            }
            else if ($(this).attr('id') == 'newAlerts-toggle') {
              statuses.push('N');
            }
            else if ($(this).attr('id') == 'pendingAlerts-toggle') {
              statuses.push('P');
            }
            else if ($(this).attr('id') == 'pastAlerts-toggle') {
              statuses.push('C');
            }
          }
        });

        locations = $filter("locationsByStatusAndAgencyDispatcher")($rootScope.alerts, statuses);
        for (var i = 0; i < locations.length; i++) {
          var tempMarker = new google.maps.Marker();
          tempMarker.setPosition(new google.maps.LatLng(locations[i].latitude, locations[i].longitude));
          tempMarker.setIcon('/media/static/shieldcommand/img/NewUserPin.png');
          tempMarker.setMap(googleMap);
          scope.tempMapMarkers.push(tempMarker);
        };
      }
    },
  }
}]);
