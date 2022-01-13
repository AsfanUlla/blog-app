var port = "";
if (window.location.port > 0){
    port = ":" + window.location.port;
}
var c_host = window.location.protocol + "//" + window.location.hostname + port;

function request(url, typ, data, callback, ele=null, return_message=false, show_msg=true){

    if(ele != null){
        $(ele).addClass('disabled loading');
    }

    var request = new XMLHttpRequest();
    request.addEventListener("progress", progress);
    request.addEventListener("load", load_error);
    request.addEventListener("error", load_error);
    request.addEventListener("abort", abort);
    request.addEventListener("timeout", timeout);
    request.open(typ, c_host + url);
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(JSON.stringify(data));

    var req = null;

    
    function progress(evt) {
        //req = JSON.parse(this.responseText);
        if(ele != null){
            $(ele).addClass('disabled loading');
        }
    }

    function abort(evt) {
        //req = JSON.parse(this.responseText);
        if(show_msg){
            msg(mbdy="Request Aborted");
        }
        if(ele != null){
            $(ele).removeClass('disabled loading');
        }
    }

    function timeout(evt) {
        //req = JSON.parse(this.responseText);
        if(show_msg){
            msg(mbdy="Request Timeout");
        }
        if(ele != null){
            $(ele).removeClass('disabled loading');
        }
    }

    function load_error(e){
        if(ele != null){
            $(ele).removeClass('disabled loading');
        }
        if (this.readyState === 4){
            if(this.status > 0){
                response = JSON.parse(this.response);
                if (this.status < 299){
                    if(response.data["success"]){
                        callback(response);
                    }
                    if(return_message === false){
                        if(show_msg){
                            msg(response.data["success"], response.message);
                        }
                    }
                } else if(this.status >= 400 && this.status < 499){
                    if(show_msg){
                        msg(false, response.detail);
                    }
                } else {
                    if(show_msg){
                        msg(false, "Internal server error");
                    }
                }
            } else{
                if(show_msg){
                    msg(false, "Check your Network and try again");
                }
            }
        }
    }
    
}

function getParameterByName(name, url) {
    name = name.replace(/[\[\]]/g, '\\$&');
    var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, ' '));
}

function msg(mhdr=false, mbdy){
    var hdr="";
    if(mhdr){
        hdr = "<i class='massive check icon' style='color:green;'></i><br/>SUCCESS";
    } else {
        hdr = "<i class='massive x icon icon' style='color:red;'></i><br/>ERROR";
    }
    $("#mhdr").html(hdr);
    $("#mbod").html(mbdy);
    $('.ui.basic.msg.modal').modal({closable  : true}).modal('show');
}
