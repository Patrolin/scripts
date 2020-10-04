// ==UserScript==
// @name         TeamsWebhook
// @namespace    http://fis.hys.cz
// @version      1.3
// @description  Send Teams notifications to Discord Webhooks
// @author       Patrolin
// @match        https://teams.microsoft.com/*
// @grant        none
// @run-at       document-start
// ==/UserScript==

(function() {
    'use strict';

    function setNotificationCallback(callback) {
        var OldNotify = window.Notification;
        var newNotify = function(title, opt){
            callback(title, opt);
            return new OldNotify(title, opt);
        };
        newNotify.requestPermission = OldNotify.requestPermission.bind(OldNotify);
        Object.defineProperty(newNotify, 'permission', {
            get: function(){
                return OldNotify.permission;
            }
        });
        window.Notification = newNotify;
    }
    var webHookURL = //...
    function discord_message(message) {
        var xhr = new XMLHttpRequest();
        xhr.open("POST", webHookURL, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(message));
    }
    // Your code here...
    console.log(1);
    console.warn(1);
    console.error(1);
    setNotificationCallback(function(t, o){
        var username = ''+t;
        var content = ''+o.body;
        var avatar_url = 'http://spse.cz/template/images/logo.png';
        var send = username && (username !== 'Soubor se nestáhl.') && !(username.startsWith('Assignment returned')) && !(content.startsWith('Assignment returned'));
        console.log(t, o, username, content, send);
        if(send){
            discord_message({
                'username': username,
                'content': content,
                'avatar_url': avatar_url,
            });
        }
    })
})();
