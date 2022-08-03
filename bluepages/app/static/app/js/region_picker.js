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


map.on('singleclick', function(e) {
    map.forEachFeatureAtPixel(e.pixel, function (f) {
        const selIndex = selected.indexOf(f);
        if (selIndex < 0) {
            selected.push(f);
            f.setStyle(selectedStyleFunction(f));
        } else {
            selected.splice(selIndex, 1);
            f.setStyle(undefined);
        }
    });

    // manage 'selected codes' box now.
    updateSelectedRegionCodes();

});

$.ajax({
    // url:'/regions.json',
    url:'/static/app/data/regions.json',
    dataType: 'json'
})
.done(function(data) {
    var features = new ol.format.GeoJSON().readFeatures(data);
    VectorSource.addFeatures(features);

    
});
