var port = "";
if (window.location.port > 0){
    port = ":" + window.location.port;
}
var c_host = window.location.protocol + "//" + window.location.hostname + port;

function request(url, typ, data, callback){
    var request = new XMLHttpRequest();
    request.addEventListener("load", callback);
    request.addEventListener("error", callback);
    request.open(typ, c_host + url);
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(JSON.stringify(data));

    var req = null;

    /*
    function succ(evt) {
        req = JSON.parse(this.responseText);
    }

    function err(evt) {
        req = JSON.parse(this.responseText);
    }
    */

}

function getParameterByName(name, url) {
    name = name.replace(/[\[\]]/g, '\\$&');
    var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, ' '));
}
