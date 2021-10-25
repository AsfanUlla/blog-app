$(document).ready(function() {

    $('.ui.checkbox').checkbox();

    $('.ui.form.host').form({
        fields: {
            host: {
                identifier:'host',
                rules:[
                    {
                        type: 'empty',
                        prompt: 'Field cannot be empty'
                    }
                ]
            }
        },
        inline : true,
        on : 'blur'
    });

    $('.ui.basic.hform.modal').modal({
        closable  : false,
        inverted: true,
        blurring: true,
        onDeny    : function(){
            $('.ui.form.host').trigger("reset");
        },
        onApprove : function() {
            $('.ui.form.host').trigger("submit");
            return false;
        }
    });

    $('.button.addhost').click(function(e){
        $('.ui.basic.hform.modal').modal('show');
    });

    function h_c(e){
        if (this.readyState === 4){
            response = JSON.parse(this.response);
            if (this.status < 299){
                alert(response.message);
                $('.ui.basic.hform.modal').modal('hide');
                $('.ui.form.host').trigger("reset");
                location.reload();
            } else if(this.status >= 400 && this.status < 499){
                alert(response.detail);
            } else {
                alert("Internal server error");
            }
        }
    }

    $('.ui.form.host').submit(function(e){
        e.preventDefault();
        $('.ui.form.host').form('validate form');
        if($('.ui.form.host').form('is valid')){
            var enabled = false;
            if ($(this).find("input[name=enabled]").is(":checked")) {
                enabled = true;
            }
            var values = {
                "host": $(this).find("input[name=host]").val(),
                "enabled": enabled
            };
            request("/admin/add_host", 'POST', values, h_c);
        }
    });

    $('.button.host_edit').on('click', function() {
        var $row = $(this).closest('tr');
        var $columns = $row.find('td');
    
        var values = {};
        
        $.each($columns, function(i, item) {
            if (i == 1){
                values["host"] = item.innerHTML.trim();
            } else if(i == 2){
                values["enabled"] = (item.innerHTML.trim() === 'true');
            }
        });

        $('.ui.form.host').find("input[name=host]").val(values["host"]);
        $('.ui.form.host').find("input[name=enabled]").prop("checked", values['enabled']);
        $('.ui.basic.hform.modal').modal('show');        

    });

});