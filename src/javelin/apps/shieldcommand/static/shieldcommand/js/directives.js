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
});
