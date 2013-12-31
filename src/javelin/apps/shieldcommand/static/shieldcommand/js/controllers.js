'use strict';

/* Controllers */

angular.module('shieldCommand.controllers', [])

.controller('CommandAlertController', ['$scope', function($scope) {

	$scope.sendCommandAlertMessage = function() {
		$scope.dismiss();
	}

}])

.controller('UserProfileController', ['$rootScope', '$scope', 'alertService', function($rootScope, $scope, alertService) {

	$scope.currentProfile = null;
	$scope.activeAlert = null;
	$scope.isProfileVisible = false;

	$scope.toggle = function() {
		$scope.isProfileVisible = !$scope.isProfileVisible;
	}

	$scope.$on('toggleProfile', function() {
		$scope.toggle();
	});

	$scope.$on('toggleProfileOpen', function() {
		$scope.activeAlert = alertService.activeAlert;
		alertService.getUserProfileForActiveAlert(function(profile) {
			$scope.currentProfile = profile;
			$scope.isProfileVisible = true;
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

	$scope.$watch('newAlertsLength', function(newLength, oldLength) {
		if (newLength > oldLength) {
			console.log(alertService.activeAgency());
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
	  		alertService.setActiveAlert(alert);
	  		if (alert.chatMessages.length > 0) {
	  			$scope.updateChatMessages();
	  		}
	  		else {
		  		alertService.getAllChatMessagesForActiveAlert(function(messages) {
		  			if (messages && messages.length > 0) {
		  				updateDisplay();
		  				newChatSound.play();
		  			};
		  			$scope.chatUpdateTimeout = setTimeout($scope.updateChatMessages, 3000);
		  		});	  			
	  		}

	  		$scope.markerSetForActiveAlert = false;	

			if (alertService.activeAlert && !$scope.markerSetForActiveAlert) {
				setMarker(alertService.activeAlert.location);
				$scope.markerSetForActiveAlert = true;
			}

  			$rootScope.$broadcast('activeAlertUpdated');
			$rootScope.$broadcast('toggleProfileOpen');
  		}
  	};

  	$scope.updateChatMessages = function () {
  		alertService.getNewChatMessagesForActiveAlert(function(messages) {
			if (messages && messages.length > 0) {
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
  	};

  	$scope.loadInitialAlerts();
}]);
