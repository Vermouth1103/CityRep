var color_list = ["#C0392B", "#E74C3C", "#9B59B6", "#8E44AD", "#2980B9", "#3498DB", "#1ABC9C", "#16A085", "#27AE60", "#2ECC71", "#F1C40F", "#F39C12", "#E67E22", "#D35400", "#BDC3C7", "#95A5A6", "#7F8C8D", "#34495E", "#E6B0AA", "#F5B7B1", "#D7BDE2", "#D2B4DE", "#A9CCE3", "#AED6F1", "#A3E4D7", "#A2D9CE", "#A9DFBF", "#ABEBC6", "#F9E79F", "#FAD7A0", "#F5CBA7", "#EDBB99"]

var struct_count = 0;
var struct_color_map = {};

var struct_map = L.map('struct_map').setView([39.059771, 115.91589], 14);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(struct_map);

$.getJSON('../../media/representation/upload/road_network/Road.json', function(data){
    console.log(data);
    var beijing_roadmap = data;

    var data_path = '../../media/representation/assign/struct_assign.json';

    var edge_mapping_path = "../../media/representation/preprocessed/edge_mapping.json"

    $.getJSON(edge_mapping_path, function(edge_mapping){
        
        fid2id = {};
        for (var key in edge_mapping){
            fid2id[edge_mapping[key]] = key
        }

        $.getJSON(data_path, function(assign_matrix){
            console.log(assign_matrix);
    
            var length_list = []
    
            var road_list = []
            for (var key in assign_matrix){
                road_list = road_list.concat(assign_matrix[key]);
                length_list.push(assign_matrix[key].length);
            }
    
            length_list.sort(function(a, b){
                return b-a;
            })
    
            var num = 10;
            var theta = length_list[num];
    
            for (var key in assign_matrix){
                if (assign_matrix[key].length >= theta){
                    if (!(key in struct_color_map)){
                        struct_color_map[key] = struct_count;
                        struct_count += 1;
                    }
                }
            }
            console.log(struct_color_map)
    
            L.geoJSON(beijing_roadmap, {
                onEachFeature: function(feature, layer) {
                    layer.bindPopup(fid2id[feature.properties.FID_1].toString());
                },
                
                filter: function (feature){
                    for (var key in assign_matrix){
                        if (assign_matrix[key].indexOf(parseInt(fid2id[feature.properties.FID_1]))!=-1 && assign_matrix[key].length >= theta){
                            color = color_list[struct_color_map[key] % color_list.length];
                            return true;
                        }
                    }
                    return true;
                },
                style: function(feature){     
                    var color = "gray";
                    for (var key in assign_matrix){
                        if (assign_matrix[key].indexOf(parseInt(fid2id[feature.properties.FID_1]))!=-1 && assign_matrix[key].length >= theta){
                            color = color_list[struct_color_map[key] % color_list.length];
                            break;
                        }
                    }
                    return {color: color};             
                }
            }).addTo(struct_map);
        });
    });
});


var function_count = 0;
var function_color_map = {};

var function_map = L.map('function_map').setView([39.059771, 115.91589], 14);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(function_map);

$.getJSON('../../media/representation/upload/road_network/Road.json', function(data){
    console.log(data);
    var beijing_roadmap = data;

    var data_path = '../../media/representation/assign/function_assign.json';

    var edge_mapping_path = "../../media/representation/preprocessed/edge_mapping.json"

    $.getJSON(edge_mapping_path, function(edge_mapping){
        
        fid2id = {};
        for (var key in edge_mapping){
            fid2id[edge_mapping[key]] = key
        }

        $.getJSON(data_path, function(assign_matrix){
            console.log(assign_matrix);
    
            var length_list = []
    
            var road_list = []
            for (var key in assign_matrix){
                road_list = road_list.concat(assign_matrix[key]);
                length_list.push(assign_matrix[key].length);
            }
    
            length_list.sort(function(a, b){
                return b-a;
            })
            // console.log(length_list)
    
            var num = 7;
            var theta = length_list[num];
    
            for (var key in assign_matrix){
                if (assign_matrix[key].length >= theta){
                    if (!(key in function_color_map)){
                        function_color_map[key] = function_count;
                        function_count += 1;
                    }
                }
            }
            console.log(function_color_map)
    
            L.geoJSON(beijing_roadmap, {
                onEachFeature: function(feature, layer) {
                    layer.bindPopup(fid2id[feature.properties.FID_1].toString());
                },
                
                filter: function (feature){
                    for (var key in assign_matrix){
                        if (assign_matrix[key].indexOf(parseInt(fid2id[feature.properties.FID_1]))!=-1 && assign_matrix[key].length >= theta){
                            color = color_list[function_color_map[key] % color_list.length];
                            return true;
                        }
                    }
                    return true;
                },
                style: function(feature){     
                    var color = "gray";
                    for (var key in assign_matrix){
                        if (assign_matrix[key].indexOf(parseInt(fid2id[feature.properties.FID_1]))!=-1 && assign_matrix[key].length >= theta){
                            color = color_list[function_color_map[key] % color_list.length];
                            break;
                        }
                    }
                    return {color: color};             
                }
            }).addTo(function_map);
        });
    });
});


// var mypop = L.popup();
// struct_map.on('click', function(e) {
//     console.log(e)
//     var content = e.latlng.toString();
//     mypop.setLatLng(e.latlng)
//         .setContent(content)
//         .openOn(struct_map);
// });
// function_map.on('click', function(e) {
//     console.log(e)
//     var content = e.latlng.toString();
//     mypop.setLatLng(e.latlng)
//         .setContent(content)
//         .openOn(function_map);
// });