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

.directive('mapControls', ['$filter', '$rootScope', 'alertService', function($filter, $rootScope, alertService) {
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

      scope.zoomToMarker = function(marker) {
        googleMap.setZoom(18);
        googleMap.setCenter(new google.maps.LatLng(marker.latLng.lat(), marker.latLng.lng()));
        for (var i = 0; i < scope.tempMapMarkers.length; i++) {
           if(scope.tempMapMarkers[i].position.equals(marker.latLng)) {
            $rootScope.$broadcast('alertPinClicked', scope.tempMapMarkers[i].alertID);
           }
        };
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
          if (locations[i]) {
            var tempMarker = new google.maps.Marker();
            tempMarker.alertID = locations[i].alertID;
            tempMarker.setPosition(new google.maps.LatLng(locations[i].location.latitude, locations[i].location.longitude));
            tempMarker.setIcon("/media/static/shieldcommand/img/" + locations[i].alertType.charAt(0).toUpperCase() + locations[i].alertType.substr(1).toLowerCase() + "UserPin.png");
            tempMarker.setTitle(locations[i].title);
            tempMarker.setMap(googleMap);
            scope.tempMapMarkers.push(tempMarker);
            google.maps.event.addListener(tempMarker, 'click', scope.zoomToMarker)
          };
        };
      }
    },
  }
}])

.directive('alertChatWindow', ['$rootScope', 'alertService', function($rootScope, alertService) {
   return {
      restrict: 'A',
      template: "<div class=\"alert-option chat\" ng-class=\"{newChat: alert.hasNewChatMessage}\">\n    <i class=\"icon-chat_bubble\" ng-click=\"toggleChat()\"></i>\n   <div class=\"arrow-left hide\"></div> <div class=\"chat-panel panel panel-default hide\">\n        <div class=\"panel-heading\">Chat with {{ alert.agencyUserMeta.getFullName() }}<span class=\"glyphicon glyphicon-remove pull-right\" ng-click=\"closeChat()\"></span></div>\n        <div class=\"panel-body\">\n            <div class=\"chat-messages\">\n                <div class=\"message-container {{ isDispatcherClass(message.senderID) }}\" ng-repeat=\"message in chatMessages() | orderBy:'timestamp'\">\n                        <div class=\"message-content\"><span class=\"message-sender\">{{ senderName(message.senderID) }}:</span> {{ message.message }}</div>\n                        <div class=\"message-timestamp\">{{ message.timestamp * 1000 | date:'MM-dd HH:mm:ss' }}</div>\n                </div>\n            </div>\n            <div class=\"message-box\">\n                <textarea ng-model=\"newChatMessage\" placeholder=\"Enter message here...\"></textarea>\n            </div> \n        </div> \n    </div>\n</div>",
      scope: {
        alert: "=",
      },
      link: function(scope, element, attr) {
        scope.adjustForProfile = false;
        scope.chatIsVisible = false;
        element.find('.message-box').keypress(function (e) {
          if (e.which == 13) {
            var chatMessageText = scope.newChatMessage;
            scope.newChatMessage = '';
            alertService.sendChatMessageForActiveAlert(chatMessageText, function(success) {
              if (success) {
                $rootScope.$broadcast('chatWasSent');
              };
            });
          };
        });

        scope.$on('chatWindowOpened', function(event, alert) {
          if (!(alert.object_id === scope.alert.object_id)) {
            scope.closeChat();
          };
        });

        scope.$on('closeChatWindowForAlert', function(event, alert) {
          if ((alert.object_id === scope.alert.object_id)) {
            scope.closeChat();
          };
        });

        scope.$on('newChatMessageReceived', function(event, alert) {
          if ((alert.object_id === scope.alert.object_id)) {
            var messages = element.find('.chat-messages');
            if (messages.length > 0) {
                messages.animate({ scrollTop: element.find('.chat-messages')[0].scrollHeight }, 0);
            };
            var panel = element.find('.chat-panel');
            if (panel.hasClass('hide')) {
              scope.alert.hasNewChatMessage = true;
            }
          }
        });

        scope.$on('profileWasOpened', function () {
          scope.adjustForProfile = true;
          if (scope.chatIsVisible) {
            element.find('.chat-panel').animate({
              right: 250,
            }, 300);
          };
        });

        scope.$on('profileWasClosed', function () {
          scope.adjustForProfile = false;
          if (scope.chatIsVisible) {
            element.find('.chat-panel').animate({
              right: 15,
            }, 300);
          };          
        });

        scope.chatMessages = function() {
          if (scope.alert && (scope.alert.object_id in $rootScope.chats)) {
            return $rootScope.chats[scope.alert.object_id].messages;
          }
          else {
            return []
          }
        }

        scope.senderName = function(senderID) {
          return (senderID == Javelin.activeAgencyUser.object_id) ? Javelin.activeAgencyUser.firstName : scope.alert.agencyUserMeta.firstName;
        }

        scope.isDispatcherClass = function(senderID) {
          return (senderID == Javelin.activeAgencyUser.object_id) ? 'dispatcher' : '';
        }

        scope.closeChat = function() {
          element.find('.chat-panel').addClass('hide');         
        }

        scope.toggleChat = function() {
          var panel = element.find('.chat-panel');
          if (panel.hasClass('hide')) {
            if (scope.adjustForProfile || $rootScope.profileIsOpen) {
              panel.css({
                right: 250,
              })
            }
            else {
              panel.css({
                right: 15,
              })            
            }
            panel.removeClass('hide');
            scope.chatIsVisible = true;
            $rootScope.$broadcast('chatWindowOpened', scope.alert);
          }
          else {
            panel.addClass('hide');
            scope.chatIsVisible = false;
          }

          if (scope.alert.hasNewChatMessage) {
            scope.alert.hasNewChatMessage = false;
          };
        }
      }
   } 
}]);
