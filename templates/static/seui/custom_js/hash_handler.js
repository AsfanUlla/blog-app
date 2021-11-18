$(document).ready(function() {
    function scroll(hashe){
        var target = $(hashe);
        headerHeight = 66.6333;
        target = target.length ? target : $('[name=' + hashe.slice(1) +']');
        if (target.length) {
            $('html,body').stop().animate({
                scrollTop: target.offset().top - 85
            }, 'linear');
        }
    }

    $('a[href*="#"]:not([href="#"])').click(function(e) {
        if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') || location.hostname == this.hostname) {
            scroll(this.hash);
        }
    });

    var hashx= window.location.hash
    if ( hashx == '' || hashx == '#' || hashx == undefined ) {
        return false;
    } else{
        scroll(hashx);
    }

}); 