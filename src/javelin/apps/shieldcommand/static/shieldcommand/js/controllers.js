'use strict';

/* Controllers */

angular.module('shieldCommand.controllers', []).
  controller('AlertsListController', ['$scope', '$filter', 'alertService', function($scope, $filter, alertService) {

  	function updateAlerts(alerts) {
		$scope.alerts = alerts;
		updateDisplay();
  	};

  	function updateDisplay() {
		$scope.myAlertsLength = $filter("filter")($scope.alerts, {status: 'A'}).length;
		$scope.newAlertsLength = $filter("filter")($scope.alerts, {status: 'N'}).length;
		$scope.pendingAlertsLength = $filter("filter")($scope.alerts, {status: 'P'}).length;
		$scope.completedAlertsLength = $filter("filter")($scope.alerts, {status: 'C'}).length;
		$scope.$apply();
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

  	$scope.alertClicked = function(index) {
  		console.log(index + " clicked");
  	};

  	$scope.acceptClicked = function(url) {
  		for (var i = 0; i < $scope.alerts.length; i++) {
  			if ($scope.alerts[i].url === url) {
		  		$scope.alerts[i].status = 'A';
		  		updateDisplay();
		  		break;
  			}
  		};
  	};

  	$scope.loadInitialAlerts();

}]);
