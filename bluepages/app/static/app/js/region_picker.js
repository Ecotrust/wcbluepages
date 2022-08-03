const VectorSource = new ol.source.Vector({
    features: []
});

const vectorLayer = new ol.layer.Vector({
    source: VectorSource,
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
