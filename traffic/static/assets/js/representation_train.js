var csrftoken = $.cookie('csrftoken');
function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$(document).ready(function(){
    $('.upload-btn').click(function(e){
        e.preventDefault();
        // 构建FormData对象
        var form_data = new FormData();
        form_data.append('file', $("#"+e.target.id).parent().find('#id_file')[0].files[0]);
        form_data.append('type', $("#"+e.target.id).parent().find('#id_type').val());
        
        $.ajax({
            url: '/traffic/representation_upload/',
            data: form_data, 
            type: 'post',
            processData:false,
            contentType:false,
            dataType: 'json',
            traditional: true,
            // 获取POST所需的csrftoken
            beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }},
            success: function (data) {
                console.log(data);
                if(data['error_msg']) {
                    var content = '<li>'+data['error_msg']+'</li>';
                    $("#"+e.target.id.replace("btn", "error")).html(content);
                }
                else{
                    var content= '<thead><tr>' +
                    '<th>Name and URL</th>' +
                    '<th>Size</th>' +
                    '<th>Data Type</th>' +
                    '</tr></thead><tbody>';

                    $.each(data, function(i, item) {
                        console.log(i ,item)
                        if (i==0){
                            window.road_network_path = item
                        }
                        content = content +
                        '<tr><td>' +
                        "<a href= ' " +
                        item['url'] +
                        " '> " +
                        item['url'] +
                        '</a></td><td>' +
                        item['size'] +
                        '</td><td>' +
                        item['type'] +
                        '</td><tr>'
                    });
                    content = content + "</tbody>";
                    $("#"+e.target.id.replace("btn", "result")).parent().css("display", "block")
                    $("#"+e.target.id.replace("btn", "result")).html(content);
                }
            },
        });
    });

    $('#submit-btn').click(function(e){
        e.preventDefault()
        var form_data = new FormData();
        form = $("#"+e.target.id).parent().parent().parent();
        form_data.append('road_num', form.find('#road_num').val());
        form_data.append('road_dim', form.find('#road_dim').val());
        form_data.append('region_num', form.find('#region_num').val());
        form_data.append('region_dim', form.find('#region_dim').val());
        form_data.append('zone_num', form.find('#zone_num').val());
        form_data.append('zone_dim', form.find('#zone_dim').val());
        form_data.append('epochs', form.find('#epochs').val());
        form_data.append('batch_size', form.find('#batch_size').val());
        form_data.append('lr', form.find('#lr').val());
        form_data.append('dropout', form.find('#dropout').val());
        $.ajax({
            url: '/traffic/representation_train/',
            data: form_data,
            type: 'POST',
            dataType: 'json',
            // 告诉jQuery不要去处理发送的数据, 发送对象。
            processData : false,
            // 告诉jQuery不要去设置Content-Type请求头
            contentType : false,
            // 获取POST所需的csrftoken
            beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }},
            success: function (data) {
                console.log(data);
                if(data['error_msg']) {
                    var content = '<li>Only json files are allowed.</li>';
                    $("#"+e.target.id.replace("btn", "error")).html(content);
                }
                else{
                    console.log($("#"+e.target.id.replace("btn", "result")).parent())
                    $("#"+e.target.id.replace("btn", "result")).parent().css("display", "block")
                    $("#"+e.target.id.replace("btn", "result")).html(content);
                }
            },
        });
    });
});


$(".parameter").focus(function(){
    var oldValue = $(this).val();
    if(oldValue == this.defaultValue){
        $(this).val("").addClass('focus-fon');
    }}).blur(function(){
        var oldValue = $(this).val();
        if(oldValue == ""){
            $(this).val(this.defaultValue).removeClass('focus-fon');
        }
    });