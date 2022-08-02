

const map = new ol.Map({
    layers: [
        new ol.layer.Tile({
            source: new ol.source.OSM
        })
    ],
    target: 'map',
    view: new ol.View({
        center: [-120,45],
        zoom: 5,
    })
});
