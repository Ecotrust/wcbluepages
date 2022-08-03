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

$.ajax({
    url:'/regions.json',
    dataType: 'json'
})
    .done(function(data) {
        var features = new ol.format.GeoJSON().readFeatures(data);
        VectorSource.addFeatures(features);
    });
