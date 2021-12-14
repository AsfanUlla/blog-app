$(document).ready(function() {

    $('.ui.checkbox').checkbox();
    $('.ui.selection.dropdown').dropdown();

    $('.ui.form.editor').form({
        fields: {
            title: {
                identifier:'title',
                rules:[
                    {
                        type: 'empty',
                        prompt: 'Please Enter article title'
                    }
                ]
            },
            hosts: {
                identifier:'hosts',
                rules:[
                    {
                        type: 'empty',
                        prompt: 'Select at least one host'
                    }
                ]
            }
        },
        inline : true,
        on : 'blur'
    });

    var data = null;
    if (article_doc){
        data = article_doc['article_data'];
    }

    const editor = new EditorJS({
        holder: 'editorjs',
        tools: { 
            header: {
                class: Header,
                inlineToolbar: ['link']
            },
            list: { 
                class: List, 
                inlineToolbar: ['link'] 
            },
            paragraph: {
                class: Paragraph,
                inlineToolbar: true
            },
            underline: Underline,
            table: {
                class: Table,
                inlineToolbar: true
            },
            warning: {
                class: Warning,
                inlineToolbar: true
            },
            code: {
                class: CodeTool,
                inlineToolbar: false
            },
            image: {
                class: ImageTool,
                config: {
                    endpoints: {
                        byFile: c_host+'/editor/upload_image'
                    },
                    field: "img"
                }
            },
            raw: {
                class: RawTool,
                inlineToolbar: false
            },
            quote: {
                class: Quote,
                inlineToolbar: true
            },
            marker: {
                class: Marker,
                inlineToolbar: false
            },
            checklist: {
                class: Checklist,
                inlineToolbar: ['link']
            },
            delimiter: {
                class: Delimiter,
                inlineToolbar: false
            },
            inlineCode: {
                class: InlineCode,
                inlineToolbar: true
            },
            embed: Embed,
        },
        data: data
    });
    
    editor.isReady.then(() => {
        $('.ui.form.editor').removeClass('loading');
        if (article_doc){
            $("#title").val(article_doc['title'])
            $("input[name=public]").prop( "checked", article_doc['published'] );
            if(article_doc['tags']){
                $("#tags").val(article_doc['tags']);
            }
            $.each(article_doc['hosts'], function(i,e){
                $(".ui.dropdown.host").find("option[value='" + e + "']").prop("selected", true);
            });
        }
    }).catch((reason) => {
        $('.ui.form.editor').removeClass('loading');
        msg(false, 'Error loading Editor Contact Admin');
        console.log(`Editor.js initialization failed because of ${reason}`);
    });

    $( ".ui.form.editor" ).submit(function( event ) {
        event.preventDefault();
    });

    $( "#e_save" ).click(function(e) {
        e.preventDefault();
        save();
    });

    $("#e_publish").click(function(e){
        e.preventDefault();
        $('.ui.form.editor').form('validate form');
        if($('.ui.form.editor').form('is valid')){
            save(pub=true);
        }
    });


    function save(pub=false){
        var article_id = null;
        var edit = false;

        const aurl = window.location.href;
        article_id = getParameterByName('article', aurl);
        if (article_id && article_id != ""){
            edit = true;
        }

        editor.save().then((outputData) => {
            if(outputData.blocks.length > 0){
                $('.ui.form.editor').addClass('loading');

                value = {
                    "title": $("#title").val(),
                    "article_data": outputData,
                    "hosts": $('#hosts').val(),
                    "edit": edit,
                    "article_id": article_id
                }

                if ($("#tags").val()){
                    value["tags"] = $("#tags").val();
                }

                function r_c(e){
                    if (this.readyState === 4){
                        response = JSON.parse(this.response);
                        if (this.status < 299){
                            if(response.data["success"]){
                                if(pub){
                                    window.location.href = response.data["article_url"];
                                }else{
                                    $("#e_publish").attr("href", response.data["article_url"]);
                                    article_id = getParameterByName('article', response.data["article_url"]);
                                    history.replaceState(response, document.title, "?article="+article_id);
                                }
                            }
                            msg(response.data["success"], response.message);
                        } else if(this.status >= 400 && this.status < 499){
                            msg(false, response.detail);
                        } else {
                            msg(false, "Internal server error");
                        }
                    }
                    $('.ui.form.editor').removeClass('loading');
                }
                request("/editor/save", 'POST', value, r_c);

            } else{
                msg(false, "Empty editor");
            }
        }).catch((error) => {
            console.log('Saving failed: ', error);
        });

    }

    /*
    $( "#e_discard" ).click(function(e) {
        e.preventDefault();
        editor.blocks.clear();
        $('.ui.form.editor')[0].reset();
        $('.ui.dropdown.host').dropdown('clear');
        window.location.href = '/editor';
    });
    */

    $( "a#mybl" ).click(function(e){
        e.preventDefault();
        $('.ui.modal.mybl').modal({closable  : true}).modal('show');
    });
    
});
