var csrftoken = $.cookie('csrftoken');
function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

let sp_layer = "";
let start_marker = "";
let end_marker = ""

var startIcon = L.icon({
    iconUrl: "/static/assets/img/start_marker.png",
    iconSize: [40, 40], // size of the icon
    iconAnchor: [20, 40]
});

var endIcon = L.icon({
    iconUrl: "/static/assets/img/end_marker.png",
    iconSize: [40, 40], // size of the icon
    iconAnchor: [20, 40]
});

$(document).ready(function(){
    $('#upload').click(function(e){
        console.log(e);
        e.preventDefault();
        // 构建FormData对象
        var form_data = new FormData();
        form_data.append('file', $("#"+e.target.id).parent().find('#id_file')[0].files[0]);
        $.ajax({
            url: '/traffic/route_plan_upload/',
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
                    $("#error").html(content);
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
                    console.log($("#"+e.target.id.replace("btn", "result")).parent())
                    $("#result").parent().css("display", "block")
                    $("#result").html(content);
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
            url: "/traffic/route_plan_train/",
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

    $("#pred-btn").click(function(e){
        e.preventDefault();
        var form_data = new FormData();
        form = $("#"+e.target.id).parent().parent().parent().parent();
        form_data.append("start", form.find("#start").val());
        form_data.append("end", form.find("#end").val());
        $.ajax({
            url: "/traffic/route_plan/",
            data: form_data,
            type: "POST",
            dataType: "json",
            processData: false,
            contentType: false,
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
                    console.log(data["sp"])
                    if(sp_layer!=""){
                        mymap.removeLayer(sp_layer)
                        mymap.removeLayer(start_marker)
                        mymap.removeLayer(end_marker)
                    }
                    sp_layer = L.geoJSON(roadmap, {
                        onEachFeature: function(feature, layer) {
                            layer.bindPopup(fid2id[feature.properties.FID_1].toString());
                        },
                        
                        filter: function (feature){
                            if(data["sp"].indexOf(parseInt(fid2id[feature.properties.FID_1]))!=-1){
                                return true;
                            }
                            else{
                                return false;
                            }
                        },
                        style: function(feature){     
                            var color = "gray";
                            var weight = 1;
                            if(data["sp"].indexOf(parseInt(fid2id[feature.properties.FID_1]))!=-1){
                                if(data["sp"].indexOf(parseInt(fid2id[feature.properties.FID_1]))==0){
                                    start_cor = [feature.geometry.coordinates[0][1], feature.geometry.coordinates[0][0]]
                                    start_marker = L.marker(start_cor, {icon: startIcon})
                                }
                                if(data["sp"].indexOf(parseInt(fid2id[feature.properties.FID_1]))==data["sp"].length-1){
                                    end_cor = [feature.geometry.coordinates[feature.geometry.coordinates.length-1][1], feature.geometry.coordinates[feature.geometry.coordinates.length-1][0]]
                                    end_marker = L.marker(end_cor, {icon: endIcon})
                                }
                                color = "red";
                                weight = 3
                            }
                            return {"color": color, "weight": weight};             
                        }
                    })
                    sp_layer.addTo(mymap);
                    // start_marker.addTo(mymap);
                    // end_marker.addTo(mymap);
                }
            },
        })
    })
});


var mymap = L.map('mapid').setView([39.059771, 115.91589], 14);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(mymap);


var color_list = ["#C0392B", "#E74C3C", "#9B59B6", "#8E44AD", "#2980B9", "#3498DB", "#1ABC9C", "#16A085", "#27AE60", "#2ECC71", "#F1C40F", "#F39C12", "#E67E22", "#D35400", "#BDC3C7", "#95A5A6", "#7F8C8D", "#34495E", "#E6B0AA", "#F5B7B1", "#D7BDE2", "#D2B4DE", "#A9CCE3", "#AED6F1", "#A3E4D7", "#A2D9CE", "#A9DFBF", "#ABEBC6", "#F9E79F", "#FAD7A0", "#F5CBA7", "#EDBB99"]

var count = 0;
var color_map = {};
let roadmap;

$.getJSON('../../media/traffic/upload/road_network/Road.json', function(data){

    roadmap = data;

    var edge_mapping_path = "../../media/traffic/preprocessed/edge_mapping.json"

    $.getJSON(edge_mapping_path, function(edge_mapping){
        
        fid2id = {};
        for (var key in edge_mapping){
            fid2id[edge_mapping[key]] = key
        }

        L.geoJSON(roadmap, {
            onEachFeature: function(feature, layer) {
                layer.bindPopup(fid2id[feature.properties.FID_1].toString());
            },
            
            filter: function (feature){
                return true;
            },
            style: function(feature){     
                var color = "gray";
                return {color: color};             
            }
        }).addTo(mymap);
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
