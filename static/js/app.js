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
        },
        checkLogin: function(callback){
            FB.getLoginStatus(callback);
        }

    }
}]);

bikeApp.config(['$routeProvider','$locationProvider',
     function($routeProvider,$locationProvider) {
         $routeProvider.
             when('/', {
                 templateUrl: '/static/pages/welcome.html',
                 controller: 'loginController'
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
    '$scope','$http','facebook', function ($scope,$http,facebook) {
        var userid = '';
        var loginstatus = false;
        var fb_id = '';
        $scope.onpageload = function(){
                 facebook.checkLogin(function (response){
                        console.log(response);
                        if(response.status ==='connected'){
                            loginstatus = true;
                            $scope.loginform = false;
                            $scope.mysavedroutes = true;
                            fb_id = response.authResponse.userID;
                            facebook.details(function (details){
                                $scope.loginform = false;
                                $http({
                                       method: 'GET',
                                       url: '/getuserid/'+fb_id
                                }).then(function(response) {
                                       console.log(response);
                                }, function(error) {
                                       console.log(error);
                                });
                            });
                        }
                        else{
                            loginstatus = false;
                            $scope.loginform = true;
                            $scope.mysavedroutes = false;
                        }
                    });
        }
        $scope.login = function () {
            if(!loginstatus){
            facebook.login(function (loginData) {
                facebook.details(function (details) {
                    var re_details = {};
                    re_details["name"] = details["name"];
                    re_details["age"] = parseInt(details["age_range"]["min"]);
                    re_details["gender"]  = details["gender"];
                    re_details["email_id"] = details["email"];
                    re_details["fb_id"] = details["id"];
                    var req = {
                        method: 'POST',
                        url: '/adduser',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        data: JSON.stringify(re_details)
                    };
                    console.log (req);
                    $http(req).then(function (resp) {
                        console.log(resp);
                        $scope.loginform = false;
                        $http({
                        	method: 'GET',
                        	url: '/getuserid/'+re_details["fb_id"]
                        }).then(function(response) {
                            console.log(response);
                        }, function(error) {
                          	console.log(error);
                        });
                    });
                });
            });

            }else{
                facebook.details(function (details){
                    $scope.loginform = false;
                    $http({
                           method: 'GET',
                           url: '/getuserid/'+fb_id
                    }).then(function(response) {
                           console.log(response);
                    }, function(error) {
                           console.log(error);
                    });
                });
            }
        }
        $scope.logout = function () {
            facebook.logout(function (response) {
                console.log(response);
                $scope.login = true;
            });
        }
    }
]);

bikeApp.controller('RouteController', function($scope, $http) {
    var map;
    $scope.narratives = [];
    $scope.distance = 0;
    $scope.time = 0;

    $scope.getdirections = function(){
            if(map)
                map.remove();
                    var src = $scope.route.source;
                    var dest = $scope.route.destination;
                    map = L.map('map', {
                        layers: MQ.mapLayer(),
                        dragging: true
                      });


					$http({
						method: 'GET',
						url: '/getDirections/'+src+"/"+dest
					}).then(function(response) {
					    console.log(response);
					    $scope.narratives = response.data.narratives;
					    var control = L.Routing.control({
                                             waypoints: response.data.lat_long,
                                             draggableWaypoints: false,
                                             show: false,
                                             createMarker: function(i,waypoints,n){
                                                if(i==0||i==n-1)
                                                    return L.marker(waypoints.latLng);
                                               }
                                           }).addTo(map);
					}, function(error) {
						console.log(error);
					});

	}
});