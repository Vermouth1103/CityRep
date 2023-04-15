var csrftoken = $.cookie('csrftoken');
function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$(document).ready(function(){
    $('#login-btn').click(function(e){
        e.preventDefault();
        // 构建FormData对象
        var form_data = new FormData();
        form_data.append('username', $("#login-username").val());
        form_data.append('password', $("#login-password").val());
        $.ajax({
            url: '/login/',
            data: form_data, 
            type: 'post',
            processData: false,
            contentType: false,
            dataType: 'json',
            traditional: true,
            // 获取POST所需的csrftoken
            beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }},
            success: function (data) {
                console.log(data);
            }
        });
    });
});