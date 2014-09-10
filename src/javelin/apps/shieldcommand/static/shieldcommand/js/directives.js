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
     restrict: 'E',
     transclude: true,
     replace: true,
     template: '<div class="modal fade" id="markAlertComplete" tabindex="-1" role="dialog" aria-labelledby="markAlertCompleteLabel" aria-hidden="true">'
            + '    <div class="modal-dialog">'
            + '        <div class="modal-content">'
            + '         <div ng-if="alert.disarmedTime != undefined">'
            + '            <div class="modal-header">'
            + '                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>'
            + '                <h4 class="modal-title" id="markAlertCompleteLabel">Complete Alert</h4>'
            + '            </div>'
            + '            <div class="modal-body">'
            + '                <p>Are you sure you would like to set status as complete?</p>'
            + '            </div>'
            + '            <div class="modal-footer">'
            + '                <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>'
            + '                <button type="button" class="btn btn-primary" ng-click="markComplete()">Mark Completed</button>'
            + '            </div>'
            + '         </div>'
            + '         <div ng-if="alert.disarmedTime == undefined">'
            + '            <div class="modal-header modal-header-warning">'
            + '                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>'
            + '                <h4 class="modal-title" id="markAlertCompleteLabel"><span class="glyphicon glyphicon-warning-sign"></span> Warning!</h4>'
            + '            </div>'            
            + '            <div class="modal-body">'
            + '                <p><strong>{{ alert.agencyUserMeta.getFullName() }} has not disarmed the alert and may not be safe.</strong></p>'
            + '                <p>Are you sure you would like to complete this alert? If so, check the override box below to enable completion button.</p>'
            + '            </div>'          
            + '            <div class="modal-footer">'
            + '                <div class="checkbox pull-left">'
            + '                    <label>'
            + '                      <input ng-model="override" ng-init="override=false" type="checkbox"> Override'
            + '                    </label>'
            + '                </div>'              
            + '                <button type="button" class="btn btn-default" data-dismiss="modal" ng-click="override=false">Cancel</button>'
            + '                <button type="button" class="btn btn-danger" ng-class="{disabled: !override}" ng-click="markComplete();override=false;">I understand, mark completed</button>'
            + '            </div>'
            + '         </div>'            
            + '        </div><!-- /.modal-content -->'
            + '    </div><!-- /.modal-dialog -->'
            + '</div>',
     scope: {
      alert: '=',
      markComplete: '&',
     },
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
      template: '<div class="alert-option chat" ng-class="{newChat: alert.hasNewChatMessage}">'
                + '    <i id="chat-icon-{{ alert.object_id }}" class="icon-chat_bubble" ng-if="alert.agencyUser" ng-click="toggleChat()"></i>'
                + '   <div class="arrow-left hide"></div> <div class="chat-panel panel panel-default hide">'
                + '        <div class="panel-heading">{{ truncateAgencyUserName(alert.agencyUserMeta.getFullName()) }}<span class="glyphicon glyphicon-remove pull-right" ng-click="closeChat()"></span></div>'
                + '        <div class="panel-body">'
                + '            <div class="chat-messages">'
                + '                <div class="message-container {{ isDispatcherClass(message.senderID) }}" ng-repeat="message in chatMessages() | orderBy:\'timestamp\'">'
                + '                        <div class="message-content"><span class="message-sender">{{ senderName(message.senderID) }}:</span> {{ message.message }}</div>'
                + '                        <div class="message-timestamp">{{ message.timestamp * 1000 | date:\'MM-dd HH:mm:ss\' }}</div>'
                + '                </div>'
                + '            </div>'
                + '            <div class="message-box">'
                + '                <textarea ng-model="newChatMessage" placeholder="Enter message here..."></textarea>'
                + '            </div> '
                + '        </div> '
                + '    </div>'
                + '</div>',
      scope: {
        alert: "=",
      },
      link: function(scope, element, attr) {
        scope.adjustForProfile = false;
        scope.chatIsVisible = false;
        element.find('.message-box').keypress(function (e) {
          if (e.which == 13 && scope.newChatMessage) {
            var chatMessageText = scope.newChatMessage;
            scope.newChatMessage = '';
            scope.sendMessage(chatMessageText);
          }
          else if (e.which == 13 && !scope.newChatMessage) {
            $(this).find("textarea").val("");
            return false;
          }
        });

        scope.truncateAgencyUserName = function(fullName) {
          var nameString = "Chat with " + fullName;
          if (nameString.length >= 27) {
            nameString = nameString.substr(0, 24) + "...";
          }
          return nameString;
        }

        scope.sendMessage = function(message) {
          alertService.sendChatMessageForActiveAlert(message, function(success) {
            if (success) {
              $rootScope.$broadcast('chatWasSent');
            }
            else {
              if (confirm("Your chat message failed to send. Try again?")) {
                scope.sendMessage(message);
              }
              else {
                scope.newChatMessage = message;
              }
            }
          });
        }

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
		$rootScope.$apply();
            }
          }
        });

        scope.$on('profileWasOpened', function () {
          scope.adjustForProfile = true;
          if (scope.chatIsVisible) {
            element.find('.chat-panel').animate({
              right: 250,
            }, 333);
          };
        });

        scope.$on('profileWasClosed', function () {
          scope.adjustForProfile = false;
          if (scope.chatIsVisible) {
            element.find('.chat-panel').animate({
              right: 15,
            }, 333);
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
          if (senderID == scope.alert.agencyUserMeta.object_id) {
            return scope.alert.agencyUserMeta.firstName;
          }
          else if (scope.alert && scope.alert.agencyDispatcherName){
            var nameTokens = scope.alert.agencyDispatcherName.split(" ");
            if (nameTokens.length > 0) {
              return nameTokens[0];
            }
          }
          return "Dispatcher";
        }

        scope.isDispatcherClass = function(senderID) {
          return (senderID == scope.alert.agencyUserMeta.object_id) ? '' : 'dispatcher';
        }

        scope.closeChat = function() {
          element.find('.chat-panel').addClass('hide');         
        }

        scope.toggleChat = function() {
          var panel = element.find('.chat-panel');
          if (panel.hasClass('hide') && scope.alert.agencyUser) {
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
