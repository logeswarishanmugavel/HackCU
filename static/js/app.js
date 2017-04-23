'use strict';

var bikeApp = angular.module('bikeApp', [
    'facebook', 'ngRoute'
 ]);

bikeApp.config(['$routeProvider','$locationProvider','FacebookProvider',
     function($routeProvider,$locationProvider,FacebookProvider) {
         $routeProvider.
             when('/', {
                 templateUrl: '/static/pages/welcome.html'
             }).
             when('/directions', {
                 templateUrl: '/static/pages/directions.html',
                 controller: 'RouteController'
             }).
             otherwise({
                 redirectTo: '/'
             });

         $locationProvider.hashPrefix('');
         FacebookProvider.init('405452559812718')
    }]);

bikeApp.controller('loginController',[
    '$scope','Facebook', function ($scope,Facebook) {
        $scope.beforeloginnavbar = true;
        $scope.afterloginnavbar = false;
        $scope.login = function () {
            Facebook.login(function (response) {
                console.log(response);
                $scope.beforeloginnavbar = false;
                $scope.afterloginnavbar = true;
            });
        }
    }
]);

bikeApp.controller('RouteController', function($scope, $http) {

    $scope.route = {};

    /*
    $scope.getdirections = function(){
					$http({
						method: 'POST',
						url: '/getdirections',
						data: $.param($scope.route),
						headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
					}).then(function(response) {
					    console.log(response);
						$scope.route = {}
					}, function(error) {
						console.log(error);
					});
	}
	*/
});