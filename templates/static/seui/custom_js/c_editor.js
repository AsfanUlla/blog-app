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
    var edit = false;
    if (article_doc){
        $("#title").val(article_doc['title']).prop('disabled', true);
        $("input[name=public]").prop( "checked", article_doc['published'] );
        if(article_doc['tags']){
            $("#tags").val(article_doc['tags']);
        }

        $.each(article_doc['hosts'], function(i,e){
            $("#hosts option[value='" + e + "']").prop("selected", true);
        });

        data = article_doc['article_data'];
        edit = true;
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
        console.log('Editor.js is ready to work!');
    }).catch((reason) => {
        console.log(`Editor.js initialization failed because of ${reason}`);
    });

    $( ".ui.form.editor" ).submit(function( event ) {
        event.preventDefault();
    });

    $( "#e_save" ).click(function(e) {
        e.preventDefault();

        $('.ui.form.editor').form('validate form');
        if($('.ui.form.editor').form('is valid')){
            editor.save().then((outputData) => {
                if(outputData.blocks.length > 0){

                    var published = false;
                    if ($("input[name=public]").is(":checked")) {
                        published = true;
                    }

                    value = {
                        "title": $("#title").val(),
                        "article_data": outputData,
                        "published": published,
                        "hosts": $('#hosts').val(),
                        "edit": edit
                    }

                    if ($("#tags").val()){
                        value["tags"] = $("#tags").val();
                    }

                    function r_c(e){
                        if (this.readyState === 4){
                            response = JSON.parse(this.response);
                            if (this.status < 299){
                                alert(response.message);
                                editor.blocks.clear();
                                $('.ui.form.editor')[0].reset();
                            } else if(this.status >= 400 && this.status < 499){
                                alert(response.detail);
                            } else {
                                alert("Internal server error");
                            }
                        }
                    }
                    request("/editor/save", 'POST', value, r_c);

                } else{
                    alert("Empty editor");
                }
            }).catch((error) => {
                console.log('Saving failed: ', error);
            });
        }
    });

    $( "#e_discard" ).click(function(e) {
        e.preventDefault();
        editor.blocks.clear();
        $('.ui.form.editor')[0].reset();
    });
    
});