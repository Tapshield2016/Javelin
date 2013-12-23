'use strict';

/* Controllers */

angular.module('shieldCommand.controllers', []).
  controller('AlertsListController', ['$scope', '$filter', 'alertService', function($scope, $filter, alertService) {

  	alertService.loadInitialAlerts(function(alerts) {
  		$scope.alerts = alerts;
  		$scope.myAlertsLength = $filter("filter")($scope.alerts, {status: 'A'}).length;
  		$scope.newAlertsLength = $filter("filter")($scope.alerts, {status: 'N'}).length;
  		$scope.pendingAlertsLength = $filter("filter")($scope.alerts, {status: 'P'}).length;
  		$scope.completedAlertsLength = $filter("filter")($scope.alerts, {status: 'C'}).length;
  		$scope.$apply();
  	});
  }]);
