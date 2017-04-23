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

bikeApp.config(['$routeProvider','$locationProvider',
     function($routeProvider,$locationProvider) {
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
    }]);

bikeApp.controller('loginController',[
    '$scope','facebook', function ($scope,facebook) {
        $scope.beforeloginnavbar = true;
        $scope.afterloginnavbar = false;
        $scope.login = function () {
            facebook.login(function (data) {
                console.log(data);
                $scope.beforeloginnavbar = false;
                $scope.afterloginnavbar = true;
            });
        };
        $scope.getDetails = function () {
            facebook.details(function (data) {
                console.log(data);
            });
        };
        $scope.logout = function () {
            facebook.logout(function (response) {
                console.log(response);
                $scope.beforeloginnavbar = true;
                $scope.afterloginnavbar = false;
            });
        }
    }
]);

bikeApp.controller('RouteController', function($scope, $http) {
    //var map;
    $scope.directions = [
    {"lng": -77.077957,"lat": 38.893165},
    {"lng": -77.077407,"lat": 38.893276},
    {"lng": -77.077087,"lat": 38.890857},
    {"lng": -77.077148,"lat": 38.890842},
    {"lng": -77.089424,"lat": 38.87355},
    {"lng": -77.088119,"lat": 38.867782},
    {"lng": -77.088584,"lat": 38.855186},
    {"lng": -77.08123,"lat": 38.848926}
    ];

    $scope.mapinit = function() {
          // map.off();
    }

    $scope.getdirections = function(){
                    var src = $scope.route.source;
                    var dest = $scope.route.destination;
                    var map = L.map('map', {
                        layers: MQ.mapLayer(),
                        zoom: 12
                      });

                   //var marker = L.marker([51.5, -0.09]).addTo(map);
                   var control = L.Routing.control({
                     waypoints: $scope.directions,
                     show: true,
                     waypointMode: 'snap',
                     createMarker: function() {}
                   }).addTo(map);


					$http({
						method: 'GET',
						url: '/getDirections/'+src+"/"+dest
					}).then(function(response) {
					    console.log(response);
					}, function(error) {
						console.log(error);
					});

	}
});