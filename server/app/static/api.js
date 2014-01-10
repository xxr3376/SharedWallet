$(function() {
  "use strict";

  var SERVER = 'http://localhost:5000';
  function deleteJSON(url, data, callback, failCallback) {
    $.ajax({
      type: 'DELETE',
      data: data,
      dataType: 'json',
      url: SERVER + url,
      success: callback,
      error: failCallback
    });
  }
  function postJSON(url, data, callback, failCallback) {
    $.ajax({
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify(data),
      dataType: 'json',
      url: SERVER + url,
      success: callback,
      error: failCallback
    });
  }
  window.postJSON = postJSON;
  var getToken = function(username, password, callback) {
    var expire_time = localStorage.getItem('expire_time', '');
    var token = localStorage.getItem('token', '');
    if (expire_time && token) {
      if (new Date(expire_time) > new Date()) {
        callback && callback(token);
        return;
      }
    }
    $.getJSON(SERVER + '/login', {username:username, password:password}, function(json) {
      if (json.status === 'SUCCESS') {
        localStorage.setItem('token', json.token);
        localStorage.setItem('expire_time', new Date(json.expire_time));
        callback(json.token);
      }
    });
  }
  function ensureToken(callback) {
    getToken('a', 'a', callback);
  }
  window.print = function(e) {console.log(e);};
  window.getAllUserList = function(callback) {
    $.getJSON(SERVER + '/users', function(json) {
      callback && callback(json);
    });
  };
  window.getWalletList = function(callback) {
    ensureToken(function(token) {
      $.getJSON(SERVER + '/wallets', {token:token}, function(json) {
        callback && callback(json);
      });
    });
  };
  window.newWallet = function(name, description, callback) {
    ensureToken(function(token) {
      postJSON('/wallets', {token: token, name:name, description:description}, function(json) {
        callback && callback(json);
      });
    });
  };
  window.getWallet = function(id, callback) {
    ensureToken(function(token) {
      $.getJSON(SERVER + '/wallets/' + id, {token:token}, function(json) {
        callback && callback(json);
      });
    });
  };
  window.getWalletUserList = function(wallet_id, callback) {
    ensureToken(function(token) {
      $.getJSON(SERVER + '/wallets/' + wallet_id + '/users', {token:token}, function(json) {
        callback && callback(json);
      });
    });
  };
  window.addWalletUser = function(wallet_id, user_id, role, callback) {
    ensureToken(function(token) {
      var data = {
        token: token,
        user_id: user_id,
        role: role
      };
      postJSON('/wallets/' + wallet_id + '/users', data, function(json) {
        callback && callback(json);
      });
    });
  };
  window.deleteWalletUser = function(wallet_id, user_id, callback) {
    ensureToken(function(token) {
      var data = {
        token: token,
        user_id: user_id,
      };
      deleteJSON('/wallets/' + wallet_id + '/users', data, function(json) {
        callback && callback(json);
      });
    });
  };
  window.getWalletEventList = function(wallet_id, callback) {
    ensureToken(function(token) {
      $.getJSON(SERVER + '/wallets/' + wallet_id + '/events', {token:token}, function(json) {
        callback && callback(json);
      });
    });
  };
  window.addWalletEvent = function(wallet_id, name, description, transaction, callback) {
    ensureToken(function(token) {
      var data = {
        token: token,
        name: name,
        description: description,
        transaction: transaction,
      };
      postJSON('/wallets/' + wallet_id + '/events', data, function(json) {
        callback && callback(json);
      });
    });
  };
});
