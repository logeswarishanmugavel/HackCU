'use strict';

var bikeApp = angular.module('bikeApp', [
    'ngRoute'
 ]);

bikeApp.run(function($rootScope, facebook) {
    $rootScope.Facebook = facebook;
});


bikeApp.factory('facebook', ['$window', function($window) {

    //get FB from the global (window) variable.
    var FB = $window.FB;

    // gripe if it's not there.
    if(!FB) throw new Error('Facebook not loaded');

    //make sure FB is initialized.
    FB.init({
        appId : '405452559812718',
        xfbml: true,
        version: 'v2.9'
    });

    return {
        // a me function
        login : function(callback) {
            FB.login(callback,{scope:'email,public_profile,user_friends'});
        },
        logout: function (callback) {
            FB.logout(callback);
        },
        friendslist: function (callback) {
            FB.api("/me",{fields: 'friends'},callback);
        },
        details: function (callback) {
            FB.api("/me",{fields: 'email,gender,name,age_range'},callback);
        }

    }
}]);

bikeApp.config(['$routeProvider',
     function($routeProvider) {
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
    '$scope','facebook', function ($scope,facebook) {
    '$scope','Facebook', function ($scope,Facebook) {
        $scope.beforeloginnavbar = true;
        $scope.afterloginnavbar = false;
        $scope.login = function () {
            facebook.login(function (data) {
                console.log(data);
            });
        };
        $scope.getDetails = function () {
            facebook.details(function (data) {
                console.log(data);
            });
        };
        $scope.logout = function () {
            facebook.login(function (data) {
                console.log(data);
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