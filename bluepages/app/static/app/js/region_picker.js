const getLabel = function(feature) {
    let text = feature.get('name') + "\n(" + feature.get('id') + ")";
    return text;
}

const styleFunction = function(feature) {
    var label = getLabel(feature);
    return new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: 'rgba(0,55,255,1.0)',
            width: 1,
        }),
        fill: new ol.style.Fill({
            color: 'rgba(0, 155, 255, 0.3)',
        }),
        text: new ol.style.Text({
            text: label,
            stroke: new ol.style.Stroke({
                color: 'white',
                width: 1
            }),
            font: 'bold 12px sans-serif'
        })
    });
}

const VectorSource = new ol.source.Vector({
    features: []
    // url: '/regions.json',
    // url: '/static/app/data/regions.json',
    // format: new ol.format.GeoJSON()
});

const vectorLayer = new ol.layer.Vector({
    source: VectorSource,
    style: styleFunction,
});

const map = new ol.Map({
    layers: [
        new ol.layer.Tile({
            source: new ol.source.OSM
        }),
        vectorLayer
    ],
    target: 'map',
    view: new ol.View({
        center: [
            -13803616.858365921,    // -124
            4865942.279503175       // 40 
        ],
        zoom: 5,
    })
});

// Selection logic largely taken from OL examples:
//  https://openlayers.org/en/latest/examples/select-features.html
//  https://openlayers.org/en/latest/examples/select-multiple-features.html

let selected = [];

function selectedStyleFunction(feature) {
    var label = getLabel(feature);
    let selectedStyle = new ol.style.Style({
        fill: new ol.style.Fill({
            color: 'rgba(255,255,255,0.1)'
        }),
        stroke: new ol.style.Stroke({
            color: 'rgba(255,0,255,1.0)',
            width: 2,
        }),
        text: new ol.style.Text({
            text: label,
            stroke: new ol.style.Stroke({
                color: 'white',
                width: 1
            }),
            font: 'bold 12px sans-serif'
        })
    })
    return selectedStyle;
}

let code_array = [];
// let name_array = [];
const updateSelectedRegionCodes = function() {
    code_array = [];
    // name_array = [];
    for (let i = 0; i < selected.length; i++) {
        code_array.push(selected[i].get('id'));
        // name_array.push(selected[i].get('name'));
    }
    code_array.sort();
    // name_array.sort();
    $('#region-codes').val(code_array.join(';'));
    // $('#region-name').val(name_array.join(';'));
}

const toggleFeatureSelection = function(feature)  {
    const selIndex = selected.indexOf(feature);
    if (selIndex < 0) {
        selected.push(feature);
        feature.setStyle(selectedStyleFunction(feature));
    } else {
        selected.splice(selIndex, 1);
        feature.setStyle(undefined);
    }
    // manage 'selected codes' box now.
    updateSelectedRegionCodes();
}

// Map and Form interactions:
map.on('singleclick', function(e) {
    map.forEachFeatureAtPixel(e.pixel, toggleFeatureSelection);
});

const update_filters = function() {
    let regions = vectorLayer.getSource().getFeatures();
    let filtered_regions = [];
    let states = [];
    let depths = [];

    if ($('#washington').is(":checked")) { states.push('WA')};
    if ($('#oregon').is(":checked")) { states.push('OR')};
    if ($('#california').is(":checked")) { states.push('CA')};

    if ($('#offshore').is(":checked")) { depths.push('O')};
    if ($('#middepth').is(":checked")) { depths.push('M')};
    if ($('#nearshore').is(":checked")) { depths.push('N')};

    if (states.length == 0 || states.length == 3) {
        filtered_regions = regions;
    } else {
        for (var region_idx = 0; region_idx < regions.length; region_idx++) {
            var region = regions[region_idx];
            for (let state_idx = 0;  state_idx < states.length; state_idx++) {
                var state = states[state_idx];
                if (region.get('states').indexOf(state) >= 0 && filtered_regions.indexOf(region) < 0 ) {
                    filtered_regions.push(region);
                }
            }
        }
    }

    let final_regions = [];
    if (depths.length == 0 || depths.length == 3) {
        final_regions = filtered_regions;
    } else {
        for (var region_idx = 0; region_idx < filtered_regions.length; region_idx++) {
            var region = filtered_regions[region_idx];
            for (let depth_idx = 0; depth_idx < depths.length; depth_idx++) {
                var depth = depths[depth_idx];
                if (region.get('depth') == depth && final_regions.indexOf(region) < 0) {
                    final_regions.push(region);
                }
            }
        }
    }

    if (states.length == 0 && depths.length == 0) {
        final_regions = [];
    }

    for (var region_idx = 0; region_idx < regions.length; region_idx++) {
        var region = regions[region_idx];
        if (final_regions.indexOf(region) >= 0 && selected.indexOf(region) < 0) {
            //select unselected region:
            toggleFeatureSelection(region);
        } else if (final_regions.indexOf(region) < 0 && selected.indexOf(region) >= 0) {
            // unselect previously selected region:
            toggleFeatureSelection(region);
        }
    }

}

$('#filter-boxes-wrapper :checkbox').change(update_filters);

// Load Regions onto map
$.ajax({
    // url:'/regions.json',
    url:'/static/app/data/regions.json',
    dataType: 'json'
})
.done(function(data) {
    var features = new ol.format.GeoJSON().readFeatures(data);
    VectorSource.addFeatures(features);    
});

const copyCodesToClipboard = function() {
    let codes = $('#region-codes').val();
    navigator.clipboard.writeText(codes);
    $('#copy-button').html('Codes copied!')
    window.setTimeout(function() {
        $('#copy-button').html('Copy to clipboard');
    }, 2000);
}