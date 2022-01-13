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
        data: data,
        onChange: (api, event) => {
            auto_save();
        }
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

    let previous_time = 0;
    function auto_save(){
        const d = new Date();
        let current_time = d.getTime();
        var diff = current_time - previous_time;
        if (diff > 10000){
            save(pub=false, auto=true);
            previous_time = d.getTime();
        }
    }

    function save(pub=false, auto=false){
        var article_id = null;
        var edit = false;

        const aurl = window.location.href;
        article_id = getParameterByName('article', aurl);
        if (article_id && article_id != ""){
            edit = true;
        }

        show_msg = true;
        ele='.ui.form.editor'
        if(auto){
            show_msg = false;
            ele='#e_save'
        }

        editor.save().then((outputData) => {
            if(outputData.blocks.length > 0){

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

                function r_c(response){
                    if(pub){
                        window.location.href = response.data["article_url"];
                    }else{
                        $("#e_publish").attr("href", response.data["article_url"]);
                        article_id = getParameterByName('article', response.data["article_url"]);
                        history.replaceState(response, document.title, "?article="+article_id);
                    }
                }
                request("/editor/save", 'POST', value, r_c, ele, false, show_msg);

            } else{
                if(!auto){
                    msg(false, "Empty editor");
                }
            }
        }).catch((error) => {
            console.log('Saving failed: ', error);
            if(!auto){
                msg(false, "Failed to Save");
            }
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
