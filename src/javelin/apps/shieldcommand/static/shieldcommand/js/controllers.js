'use strict';

/* Controllers */

angular.module('shieldCommand.controllers', [])

.controller('CommandAlertController', ['$scope', 'alertService', function($scope, alertService) {

	$scope.sendCommandAlertMessage = function() {
		alertService.sendMassAlert($scope.message, function(success) {
			if (success) {
				$scope.dismiss();
				$scope.message = '';
			}
			else {

			}
		});
	}

}])

.controller('UserProfileController', ['$rootScope', '$scope', 'alertService', function($rootScope, $scope, alertService) {

	$scope.currentProfile = null;
	$scope.activeAlert = null;
	$scope.isProfileVisible = false;

	$scope.toggle = function() {
		$scope.isProfileVisible = !$scope.isProfileVisible;
		if ($scope.isProfileVisible) {
			$rootScope.$broadcast('profileWasOpened');
		}
		else {
			$rootScope.$broadcast('profileWasClosed');
		}
	}

	$scope.$on('toggleProfile', function() {
		$scope.toggle();
	});

	$scope.$on('toggleProfileOpen', function() {
		$scope.activeAlert = alertService.activeAlert;
		alertService.getUserProfileForActiveAlert(function(profile) {
			$scope.currentProfile = profile;
			$scope.isProfileVisible = true;
			$rootScope.$broadcast('profileWasOpened');
		});
	});

	$scope.shouldDisplayProfileButtons = function() {
		if ($scope.activeAlert && $scope.activeAlert.status == 'A') {
			return true;
		}
		return false;
	}

	$scope.markActiveAlertAsCompleted = function() {
		$scope.activeAlert.status = 'C';		
		$scope.toggle();
		clearActiveAlertMarker();
		$scope.returnToGeofenceCenter();
		$scope.dismissMarkCompletedModal();
		alertService.markActiveAlertAsCompleted(function(data) {
			$scope.activeAlert = null;
			alertService.activeAlert = null;
			$rootScope.$broadcast('alertMarkedChange');
			$rootScope.$broadcast('alertMarkedCompleted');
		});
	}

	$scope.markActiveAlertAsPending = function() {
		$scope.activeAlert.status = 'P';
		$scope.toggle();
		$scope.dismissMarkPendingModal();
		clearActiveAlertMarker();
		alertService.markActiveAlertAsPending(function(data) {
			$scope.activeAlert = null;
			alertService.activeAlert = null;
			$rootScope.$broadcast('alertMarkedChange');
			$rootScope.$broadcast('alertMarkedPending');
		});
	}

	$scope.getAge = function(dateString) {
	    var today = new Date();
	    var birthDate = new Date(dateString);
	    var age = today.getFullYear() - birthDate.getFullYear();
	    var m = today.getMonth() - birthDate.getMonth();
	    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
	        age--;
	    }
	    return age;
	}

	$scope.returnToGeofenceCenter = function () {
		setMapCenterToDefault();
	}

	$scope.zoomToActiveAlertMarker = function () {
		if ($scope.activeAlert) {
			setMarker($scope.activeAlert.location);
		};
	}

}])

.controller('AlertsListController', ['$rootScope', '$scope', '$filter', 'alertService', function($rootScope, $scope, $filter, alertService) {

	$scope.alerts = [];
	$scope.chats = {};
	$scope.myAlertsLength = 0;
	$scope.newAlertsLength = 0;
	$scope.pendingAlertsLength = 0;
	$scope.completedAlertsLength = 0;
	$scope.currentProfile = null;
	$scope.markerSetForActiveAlert = false;
	$scope.chatUpdateTimeout = null;
	$scope.newAlertSoundInterval = null;

	$scope.$on('alertMarkedChange', function() {
		updateDisplay();
	});

	$scope.$on('alertMarkedPending', function() {
		clearTimeout($scope.chatUpdateTimeout);
	});

	$scope.$on('chatWindowOpened', function(event, alert) {
		if ((!alertService.activeAlert) || !(alert.object_id === alertService.activeAlert.object_id)) {
			$scope.alertClicked(alert);
		};
	});

	$scope.$watch('newAlertsLength', function(newLength, oldLength) {
		if (newLength > oldLength) {
			if (alertService.activeAgency() && alertService.activeAgency().loopAlertSound) {
				newAlertSound.play();
				$scope.newAlertSoundInterval = setInterval(function () {
					newAlertSound.play();
				}, 2000);
			}
			else {
				newAlertSound.play();
			}
		}
		else if (newLength == 0) {
			newAlertSound.stop();
			clearInterval($scope.newAlertSoundInterval);
		}
	});

  	function updateAlerts(alerts) {
		$scope.alerts = alerts;
		$rootScope.alerts = $scope.alerts;
		updateDisplay();
  	};

  	function updateDisplay() {
		$scope.myAlertsLength = $filter("byAgencyDispatcher")($($filter("filter")($scope.alerts, {status: 'A'}))).length;
		$scope.newAlertsLength = $filter("filter")($scope.alerts, {status: 'N'}).length;
		$scope.pendingAlertsLength = $filter("filter")($scope.alerts, {status: 'P'}).length;
		$scope.completedAlertsLength = $filter("filter")($scope.alerts, {status: 'C'}).length;

		/* Don't call apply if we're already in the middle of a digest... */
		if ($scope.$root.$$phase != '$apply' && $scope.$root.$$phase != '$digest') {
			$scope.$apply();
		}
  	};

  	$scope.loadInitialAlerts = function() {
		alertService.loadInitialAlerts(function(alerts) {
			updateAlerts(alerts);
			setTimeout($scope.getUpdatedAlerts, 3000);
		});
  	};

  	$scope.getUpdatedAlerts = function() {
  		alertService.getUpdatedAlerts($scope.alerts, function(updatedAlerts) {
  			updateAlerts(updatedAlerts);
			setTimeout($scope.getUpdatedAlerts, 3000);
  		});
  	}

  	$scope.alertClicked = function(alert) {
  		if (alert === alertService.activeAlert) {
  			$rootScope.$broadcast('toggleProfile');
  		}
  		else {
  			clearTimeout($scope.chatUpdateTimeout);
  			if (alertService.activeAlert) {
	  			$rootScope.$broadcast('closeChatWindowForAlert', alertService.activeAlert);
  			}
	  		alertService.setActiveAlert(alert);

  			$scope.initChatMessagesForActiveAlert();

	  		$scope.markerSetForActiveAlert = false;	

			if (alertService.activeAlert && !$scope.markerSetForActiveAlert) {
				setMarker(alertService.activeAlert.location);
				addressForLocation(alertService.activeAlert.location, function(address) {
					if (address) {
						alertService.activeAlert.geocodedAddress = address;
						$("#alert-address  p").html("<strong>Location:</strong> " + address);
						$("#alert-address").removeClass('hide');
					}
					else {
						$("#alert-address").addClass('hide');
					}
				});
				$scope.markerSetForActiveAlert = true;
			}

  			$rootScope.$broadcast('activeAlertUpdated');
			$rootScope.$broadcast('toggleProfileOpen');
  		}
  	};

  	$scope.initChatMessagesForActiveAlert = function() {
  		console.log(alertService.activeAlert.object_id);
  		if (alertService.activeAlert.object_id in $scope.chats) {
			alertService.activeAlert.chatMessages = $scope.chats[alertService.activeAlert.object_id];
  		}
  		else {		
			alertService.getAllChatMessagesForActiveAlert(function(messages) {
				if (messages && messages.length > 0) {
					$scope.chats[alertService.activeAlert.object_id] = messages;
					alertService.activeAlert.chatMessages = $scope.chats[alertService.activeAlert.object_id];
					updateDisplay();
					newChatSound.play();
				}
			});
  		}

		if (alertService.activeAlert.status == 'A') {
			$scope.chatUpdateTimeout = setTimeout($scope.updateChatMessages, 3000);
		}
  	}

  	$scope.updateChatMessages = function () {
  		alertService.getNewChatMessagesForActiveAlert(function(messages) {
			if (messages && messages.length > 0) {
				$scope.chats[alertService.activeAlert.object_id] = $scope.chats[alertService.activeAlert.object_id].concat(messages);
				alertService.activeAlert.chatMessages = $scope.chats[alertService.activeAlert.object_id];
				updateDisplay();
  				newChatSound.play();
			}
			$scope.chatUpdateTimeout = setTimeout($scope.updateChatMessages, 3000);
		});
  	}

    $scope.selectedClass = function(alert) {
        return alert === alertService.activeAlert ? 'selected' : undefined;
    };

  	$scope.acceptClicked = function(alert) {
  		alert.status = 'A';
  		updateDisplay();
		alertService.claimAlertForActiveUser(alert, function(data) {
			// Anything to do here?
		});

		if (alert == alertService.activeAlert) {
			$scope.initChatMessagesForActiveAlert();
		};
  	};

  	$scope.loadInitialAlerts();
}]);
