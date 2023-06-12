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

var mymap = L.map('mapid').setView([39.059771, 115.91589], 14);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(mymap);


var color_list = ["#C0392B", "#E74C3C", "#9B59B6", "#8E44AD", "#2980B9", "#3498DB", "#1ABC9C", "#16A085", "#27AE60", "#2ECC71", "#F1C40F", "#F39C12", "#E67E22", "#D35400", "#BDC3C7", "#95A5A6", "#7F8C8D", "#34495E", "#E6B0AA", "#F5B7B1", "#D7BDE2", "#D2B4DE", "#A9CCE3", "#AED6F1", "#A3E4D7", "#A2D9CE", "#A9DFBF", "#ABEBC6", "#F9E79F", "#FAD7A0", "#F5CBA7", "#EDBB99"]

var count = 0;
var color_map = {};
let roadmap;

let node_data;

$.getJSON('../../media/population/upload/road_network/Xiongan_grid.json', function(data){
    console.log(data)

    node_data = data;

    L.geoJSON(node_data, {
        pointToLayer: function (feature, latlng) {
            // 定义中心点坐标和正方形边长
            var center = latlng;
            var length = 0.003; // 单位是经纬度，这里表示正方形边长为0.1度

            // 根据中心点和边长计算正方形的四个角的坐标
            var northWest = L.latLng(center.lat - length / 2, center.lng - length / 2);
            var southEast = L.latLng(center.lat + length / 2, center.lng + length / 2);
            var southWest = L.latLng(center.lat + length / 2, center.lng - length / 2);
            var northEast = L.latLng(center.lat - length / 2, center.lng + length / 2);

            // 在地图上绘制正方形
            var square = L.polygon([northWest, northEast, southEast, southWest], {
                color: "#000", 
                weight: 1, 
                fillOpacity: 0.3, 
                fillColor: "hsl(" + 60 + ", 100%, 50%)" 
            })
            return square;
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
