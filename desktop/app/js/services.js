'use strict';

/* Services */

var services = angular.module('APIServices', ['ngResource'])
var SERVER = "http://wallet.xuxinran.me";

services.factory('TokenHandler', ['$q', '$http', function($q, $http) {
  var tokenHandler = {};
  var token = '';
  var expire_time = '';
  var userInfo = {};
  tokenHandler.login = function(username, password) {
    return $http({method: 'GET', url: SERVER + '/login?username=' + username + '&password=' + password}).
        success(function(data) {
          token = data.token;
          expire_time = new Date(data.expire_time);
          userInfo = {
            user_id: data.user_id,
            name: data.name,
            username: data.username,
          };
        });
  };
  tokenHandler.set = function(newToken) {
    token = newToken;
  }
  tokenHandler.isLoggedIn = function() {
    return !!token;
  }
  tokenHandler.get = function() {
    return token;
  };
  // wrap given actions of a resource to send auth token with every
  // request
  tokenHandler.wrapActions = function( resource, actions ) {
    // copy original resource
    var wrappedResource = resource;
    for (var i=0; i < actions.length; i++) {
      tokenWrapper( wrappedResource, actions[i] );
    };
    // return modified copy of resource
    return wrappedResource;
  };
  // wraps resource action to send request with auth token
  var tokenWrapper = function( resource, action ) {
    // copy original action
    resource['_' + action]  = resource[action];
    // create new action wrapping the original and sending token
    resource[action] = function( data, success, error){
      return resource['_' + action](
          angular.extend({}, data || {}, {token: tokenHandler.get()}),
          success,
          error
          );
    };
  };
  return tokenHandler;
}]);

services.factory('Wallet', ['$resource', 'TokenHandler', function($resource, tokenHandler) {
  var resource = $resource(SERVER + '/wallets/:walletId', {}, {
    query: {method:'GET', params:{walletId:''}, isArray:true},
    save: {method:'POST'},
  });
  resource = tokenHandler.wrapActions(resource, ['query', 'get', 'save']);
  return resource;
}]);
services.factory('WalletUser', ['$resource', 'TokenHandler', function($resource, tokenHandler) {
  var resource = $resource(SERVER + '/wallets/:walletId/users', {}, {
    query: {method:'GET', isArray:true},
    save: {method:'POST'},
  });
  resource = tokenHandler.wrapActions(resource, ['query', 'save']);
  return resource;
}]);
services.factory('Users', ['$resource', function($resource) {
  var resource = $resource(SERVER + '/users', {}, {
    query: {method:'GET', isArray:true},
  });
  return resource;
}]);
services.factory('WalletEvent', ['$resource', 'TokenHandler', function($resource, tokenHandler) {
  var resource = $resource(SERVER + '/wallets/:walletId/events/:eventId', {}, {
    query: {method:'GET', isArray:true},
    save: {method:'POST'},
  });
  resource = tokenHandler.wrapActions(resource, ['query', 'save', 'get']);
  return resource;
}]);
