var mymap = L.map('mapid').setView([39.0480479, 115.9075331], 13);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(mymap);


var color_list = ["#C0392B", "#E74C3C", "#9B59B6", "#8E44AD", "#2980B9", "#3498DB", "#1ABC9C", "#16A085", "#27AE60", "#2ECC71", "#F1C40F", "#F39C12", "#E67E22", "#D35400", "#BDC3C7", "#95A5A6", "#7F8C8D", "#34495E", "#E6B0AA", "#F5B7B1", "#D7BDE2", "#D2B4DE", "#A9CCE3", "#AED6F1", "#A3E4D7", "#A2D9CE", "#A9DFBF", "#ABEBC6", "#F9E79F", "#FAD7A0", "#F5CBA7", "#EDBB99"]

function onEachFeature(feature, layer) {
    if (feature.properties.class != "LNNode"){
        layer.bindPopup(feature.properties.id.toString());
    }
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
        console.log("fid2id")
        console.log(fid2id)

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

// var mypop = L.popup();
// mymap.on('click', function(e) {
// var content = e.latlng.toString();
// mypop.setLatLng(e.latlng)
//     .setContent(content)
//     .openOn(mymap);
// });