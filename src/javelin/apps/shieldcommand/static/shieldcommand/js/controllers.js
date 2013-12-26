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

	$scope.toggle = function() {
		$scope.isProfileVisible = !$scope.isProfileVisible;
	}

	$scope.isProfileVisible = false;

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

	$scope.markActiveAlertAsCompleted = function() {
		alertService.markActiveAlertAsCompleted(function(data) {
			$scope.dismiss();
			$rootScope.$broadcast('alertMarkedComplete');
			$scope.toggle();
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

}])

.controller('AlertsListController', ['$rootScope', '$scope', '$filter', 'alertService', function($rootScope, $scope, $filter, alertService) {

	$scope.alerts = [];
	$scope.currentProfile = null;

	$scope.$on('alertMarkedComplete', function() {
		updateDisplay();
	});

  	function updateAlerts(alerts) {
		$scope.alerts = alerts;
		updateDisplay();
  	};

  	function updateDisplay() {
		$scope.myAlertsLength = $filter("filter")($scope.alerts, {status: 'A'}).length;
		$scope.newAlertsLength = $filter("filter")($scope.alerts, {status: 'N'}).length;
		$scope.pendingAlertsLength = $filter("filter")($scope.alerts, {status: 'P'}).length;
		$scope.completedAlertsLength = $filter("filter")($scope.alerts, {status: 'C'}).length;
	
		if (alertService.activeAlert) {
			setMarker(alertService.activeAlert.location);
		}
			
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
  		alertService.getUpdatedAlerts($scope.alerts, function(updatedAlerts, changed) {
  			updateAlerts(updatedAlerts);
			setTimeout($scope.getUpdatedAlerts, 3000);
  		});
  	}

  	$scope.alertClicked = function(alert) {
  		if (alert === alertService.activeAlert) {
  			$rootScope.$broadcast('toggleProfile');
  			alertService.activeAlert = null;
  		}
  		else {
	  		alertService.setActiveAlert(alert);
  			$rootScope.$broadcast('activeAlertUpdated');
			$rootScope.$broadcast('toggleProfileOpen');	
  		}
  	};

    $scope.selectedClass = function(alert) {
        return alert === alertService.activeAlert ? 'selected' : undefined;
    };

  	$scope.acceptClicked = function(url) {
  		for (var i = 0; i < $scope.alerts.length; i++) {
  			if ($scope.alerts[i].url === url) {
		  		$scope.alerts[i].status = 'A';
		  		updateDisplay();
		  		alertService.claimAlertForActiveUser($scope.alerts[i], function(data) {
		  			// Anything to do here?
		  		});
		  		break;
  			}
  		};
  	};

  	$scope.loadInitialAlerts();
}]);
