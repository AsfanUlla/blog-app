$(document).ready(function() {
	$('.ui.form.login').form({
        fields: {
            user_email: {
                identifier:'user_email',
                rules:[
                    {
                        type: 'email',
                        prompt: 'Enter email'
                    }
                ]
            },
            passwd: {
                identifier:'passwd',
                rules:[
                    {
                        type: 'empty',
                        prompt: 'Enter password'
                    }
                ]
            }
        },
        inline : true,
        on : 'blur'
    });

    $( ".ui.form.login" ).submit(function( event ) {
        event.preventDefault();
    });

	$( "#login_s" ).click(function(e) {
        e.preventDefault();
        $('.ui.form.login').form('validate form');

        if($('.ui.form.login').form('is valid')){
	        const data = new FormData($('.ui.form.login')[0]);
	        const value = Object.fromEntries(data.entries());
            function l_c(response){
                window.location.replace(c_host + "/editor");
            }

	        request("/admin/login", 'POST', value, l_c, "#login_s", true);
    	}
	});
});
