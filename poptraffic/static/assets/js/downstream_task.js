var csrftoken = $.cookie('csrftoken');
function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$(document).ready(function(){
    $('#btn1').click(function(e){
        console.log(e);
        e.preventDefault();
        // 构建FormData对象
        var form_data = new FormData();
        form_data.append('file', $("#"+e.target.id).parent().find('#id_file')[0].files[0]);
        console.log(form_data)
        $.ajax({
            url: '/poptraffic/downstream_task/',
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

                    $.each(data["data"], function(i, item) {
                        console.log(i ,item)
                        if (i==0){
                            window.road_network_path = item
                        }
                        else{
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
                        }
                    });
                    content = content + "</tbody>";
                    console.log($("#"+e.target.id.replace("btn", "result")).parent())
                    $("#"+e.target.id.replace("btn", "result")).parent().css("display", "block")
                    $("#"+e.target.id.replace("btn", "result")).html(content);
                }
            },
        });
    });
    
    $("#submit-btn").click(function(e){
        e.preventDefault()
        var form_data = new FormData();
        form = $("#"+e.target.id).parent().parent().parent();
        form_data.append('epochs', form.find('#epochs').val());
        form_data.append('batch_size', form.find('#batch_size').val());
        form_data.append('lr', form.find('#lr').val());
        form_data.append('dropout', form.find('#dropout').val());
        console.log(form_data);
        $.ajax({
            url: "/poptraffic/route_plan/",
            data: form_data,
            type: "POST",
            dataType: "json",
            // 告诉jQuery不要去处理发送的数据, 发送对象。
            processData: false,
            // 告诉jQuery不要去设置Content-Type请求头
            contentType: false,
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
        })
    });
});



var mymap = L.map('mapid').setView([39.059771, 115.91589], 14);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(mymap);


var color_list = ["#C0392B", "#E74C3C", "#9B59B6", "#8E44AD", "#2980B9", "#3498DB", "#1ABC9C", "#16A085", "#27AE60", "#2ECC71", "#F1C40F", "#F39C12", "#E67E22", "#D35400", "#BDC3C7", "#95A5A6", "#7F8C8D", "#34495E", "#E6B0AA", "#F5B7B1", "#D7BDE2", "#D2B4DE", "#A9CCE3", "#AED6F1", "#A3E4D7", "#A2D9CE", "#A9DFBF", "#ABEBC6", "#F9E79F", "#FAD7A0", "#F5CBA7", "#EDBB99"]

function onEachFeature(feature, layer) {
    console.log(feature.properties);
    // layer.bindPopup(feature.properties.id.toString());
}
var count = 0;
var color_map = {};

$.getJSON('../../media/road_network/Road.json', function(data){
    console.log(data);
    var beijing_roadmap = data;

    var data_path = '../../media/assign/struct_fnc.json';

    var edge_mapping_path = "../../media/preprocessed_road_network/edge_mapping.json"

    $.getJSON(edge_mapping_path, function(edge_mapping){
        
        fid2id = {};
        for (var key in edge_mapping){
            fid2id[edge_mapping[key]] = key
        }
        // console.log("fid2id")
        // console.log(fid2id)

        $.getJSON(data_path, function(assign_matrix){
            console.log(assign_matrix);
    
            var length_list = []
    
            var road_list = []
            for (var key in assign_matrix){
                road_list = road_list.concat(assign_matrix[key]);
                length_list.push(assign_matrix[key].length);
            }
            // console.log(road_list);
            // console.log(length_list);
    
            length_list.sort(function(a, b){
                return b-a;
            })
            // console.log(length_list)
    
            var num = 10;
            var theta = length_list[num];
            // console.log(theta);
    
            for (var key in assign_matrix){
                if (assign_matrix[key].length >= theta){
                    if (!(key in color_map)){
                        color_map[key] = count;
                        count += 1;
                    }
                }
            }
            console.log(color_map)
    
            L.geoJSON(beijing_roadmap, {
                onEachFeature: function(feature, layer) {
                    layer.bindPopup(fid2id[feature.properties.FID_1].toString());
                },
                
                filter: function (feature){
                    for (var key in assign_matrix){
                        if (assign_matrix[key].indexOf(parseInt(fid2id[feature.properties.FID_1]))!=-1 && assign_matrix[key].length >= theta){
                            color = color_list[color_map[key] % color_list.length];
                            return true;
                        }
                    }
                    return true;
                },
                style: function(feature){     
                    // console.log(feature)
                    var color = "gray";
                    for (var key in assign_matrix){
                        if (assign_matrix[key].indexOf(parseInt(fid2id[feature.properties.FID_1]))!=-1 && assign_matrix[key].length >= theta){
                            color = color_list[color_map[key] % color_list.length];
                            break;
                        }
                    }
                    return {color: color};             
                }
            }).addTo(mymap);
        });
    });
});

var mypop = L.popup();
mymap.on('click', function(e) {
    console.log(e)
    var content = e.latlng.toString();
    mypop.setLatLng(e.latlng)
        .setContent(content)
        .openOn(mymap);
});