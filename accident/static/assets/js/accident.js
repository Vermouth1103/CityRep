var csrftoken = $.cookie('csrftoken');
function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

let speed_layer = "";

$(document).ready(function(){
    $('#upload').click(function(e){
        e.preventDefault();
        // 构建FormData对象
        var form_data = new FormData();
        form_data.append('file', $("#history_flow")[0].files[0]);
        $.ajax({
            url: '/accident/accident_upload/',
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
                    console.log(data["speed"])
                    if(speed_layer!=""){
                        mymap.removeLayer(speed_layer)
                    }
                    speed_layer = L.geoJSON(roadmap, {
                        onEachFeature: function(feature, layer) {
                            layer.bindPopup(fid2id[feature.properties.FID_1].toString());
                        },
                        
                        filter: function (feature){
                            if(Object.keys(data["speed"]).indexOf(fid2id[feature.properties.FID_1])!=-1){
                                return true;
                            }
                            else{
                                return false;
                            }
                        },
                        style: function(feature){     
                            var color = "gray";
                            if(Object.keys(data["speed"]).indexOf(fid2id[feature.properties.FID_1])!=-1){
                                flow = data["speed"][fid2id[feature.properties.FID_1]]
                                color = color_list[parseInt(flow / 5)];
                            }
                            return {"color": color};             
                        }
                    })
                    speed_layer.addTo(mymap);
                }
            },
        });
    });
    
    $("#pred").click(function(e){
        e.preventDefault()
        var form_data = new FormData();
        form = $("#pred_form");
        form_data.append('road', form.find('#road').val());
        form_data.append('time', form.find('#time').val());
        $.ajax({
            url: "/accident/accident_pre/",
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
                    console.log(data["pred_speed"])
                    if(speed_layer!=""){
                        mymap.removeLayer(speed_layer)
                    }
                    speed_layer = L.geoJSON(roadmap, {
                        onEachFeature: function(feature, layer) {
                            layer.bindPopup(fid2id[feature.properties.FID_1].toString());
                        },
                        
                        filter: function (feature){
                            if(Object.keys(data["pred_speed"]).indexOf(fid2id[feature.properties.FID_1])!=-1){
                                return true;
                            }
                            else{
                                return false;
                            }
                        },
                        style: function(feature){     
                            var color = "gray";
                            if(Object.keys(data["pred_speed"]).indexOf(fid2id[feature.properties.FID_1])!=-1){
                                flow = data["pred_speed"][fid2id[feature.properties.FID_1]]
                                color = color_list[parseInt(flow / 5)];
                            }
                            return {"color": color};             
                        }
                    })
                    speed_layer.addTo(mymap);
                }
            },
        })
    });
});


var mymap = L.map('mapid').setView([39.059771, 115.91589], 14);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(mymap);


var color_list = ["#D35400", "#E74C3C", "#E67E22", "#F39C12", "#F1C40F", "#2ECC71", "#27AE60", "#1ABC9C", "#16A085"]

var count = 0;
var color_map = {};
let roadmap;

$.getJSON('../../media/representation/upload/road_network/Road.json', function(data){

    roadmap = data;

    var edge_mapping_path = "../../media/representation/preprocessed/edge_mapping.json"

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
