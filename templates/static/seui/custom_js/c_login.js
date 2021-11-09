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
	        const lvalue = Object.fromEntries(data.entries());
            function l_c(e){
                if (this.readyState === 4){
                    response = JSON.parse(this.response);
                    if (this.status < 299){
                        if(response.data.success){
                            window.location.replace(c_host + "/editor");
                        }
                    } else if(this.status >= 400 && this.status < 499){
                        alert(response.detail);
                    } else {
                        alert("Internal server error");
                    }
                }
            }

	        request("/admin/login", 'POST', lvalue, l_c);
    	}
	});
});
