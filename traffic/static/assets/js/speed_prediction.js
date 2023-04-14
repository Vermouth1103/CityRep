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

function getColor(speed) {
    if (speed < 20) {
      return "#FF0000"; // 红色，表示拥堵
    } else if (speed < 40) {
      return "#FFA500"; // 橙色，表示缓慢
    } else if (speed < 60) {
      return "#FFFF00"; // 黄色，表示正常
    } else {
      return "#00FF00"; // 绿色，表示畅通
    }
}

$(document).ready(function(){
    $('#upload').click(function(e){
        e.preventDefault();
        // 构建FormData对象
        var form_data = new FormData();
        form_data.append('file', $('#upload_file')[0].files[0]);
        $.ajax({
            url: '/traffic/speed_prediction_upload/',
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
                    speed_layer = L.geoJSON(node_data, {
                        pointToLayer: function (feature, latlng) {

                            return L.circleMarker(latlng, {
                                radius: 4,
                                fillColor: getColor(data["speed_dict"][feature.id]),
                                color: "#000",
                                weight: 1,
                                opacity: 1,
                                fillOpacity: 0.8
                            });
                        }
                    }).addTo(mymap);
                }
            },
        });
    });

    $("#pred").click(function(e){
        e.preventDefault();
        var form_data = new FormData();
        form_data.append("pred_time", $("#pred_time").val());
        $.ajax({
            url: "/traffic/speed_prediction/",
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
                    if(speed_layer!=""){
                        mymap.removeLayer(speed_layer)
                    }
                    speed_layer = L.geoJSON(node_data, {
                        pointToLayer: function (feature, latlng) {

                            return L.circleMarker(latlng, {
                                radius: 4,
                                fillColor: getColor(data["speed_dict"][feature.id]),
                                color: "#000",
                                weight: 1,
                                opacity: 1,
                                fillOpacity: 0.8
                            });
                        }
                    }).addTo(mymap);
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

let node_data;

$.getJSON('../../media/traffic/upload/road_network/Node.json', function(data){

    node_data = data;

    L.geoJSON(node_data, {
        pointToLayer: function (feature, latlng) {
            return L.circleMarker(latlng, {
                radius: 4,
                fillColor: "#000",
                color: "#000",
                weight: 1,
                opacity: 1,
                fillOpacity: 0.8
            });
        }
    }).addTo(mymap)

});

var mypop = L.popup();
mymap.on('click', function(e) {
    console.log(e)
    var content = e.latlng.toString();
    mypop.setLatLng(e.latlng)
        .setContent(content)
        .openOn(mymap);
});
