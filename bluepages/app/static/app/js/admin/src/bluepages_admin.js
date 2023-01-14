import Map from 'ol/Map.js';
import OSM from 'ol/source/OSM.js';
import VectorSource from 'ol/source/Vector';
import VectorLayer from 'ol/layer/Vector';
import TileLayer from 'ol/layer/Tile.js';
import View from 'ol/View.js';
import Style from 'ol/style/Style';
import Stroke from 'ol/style/Stroke';
import Fill from 'ol/style/Fill';
import Text from 'ol/style/Text';
import GeoJSON from 'ol/format/GeoJSON';

var $ = require( "jquery" );

app.loadRegions = function(){
    $.ajax({
        url:'/static/app/data/regions.json',
        dataType: 'json'
    })
    .done(function(data) {
        app.regions_loaded = data;
    });
}

app.getRecordMapLabel = function(feature) {
    let text = feature.get('name');
    return text;
}

app.regionSuggestionStyle = function(feature) {
    var label = app.getRecordMapLabel(feature);
    return new Style({
        stroke: new Stroke({
            color: 'rgba(0,55,255,1.0)',
            width: 1,
        }),
        fill: new Fill({
            color: 'rgba(0, 155, 255, 0.3)',
        }),
        text: new Text({
            text: label,
            stroke: new Stroke({
                color: 'white',
                width: 1
            }),
            font: 'bold 12px sans-serif'
        })
    });
}

app.mapZoomToBufferedExtent = function(extent, buffer, map) {
    if (buffer > 1.0) {
      buffer = buffer/100.0;
    }
    let width = Math.abs(extent[2]-extent[0]);
    let height = Math.abs(extent[3]-extent[1]);
    let w_buffer = width * buffer;
    let h_buffer = height * buffer;
    let buf_west = extent[0] - w_buffer;
    let buf_east = extent[2] + w_buffer;
    let buf_south = extent[1] - h_buffer;
    let buf_north = extent[3] + h_buffer;
    let buffered_extent = [buf_west, buf_south, buf_east, buf_north];
    map.getView().fit(buffered_extent, {'duration': 1000});
}


app.createTopicMap = function(record_suggestion_id){
    if (!app.regions_loaded) {
        setTimeout(() => {
            app.createTopicMap(record_suggestion_id);
        }, 500);
    } else {
        let record_id_str = record_suggestion_id.toString();
        app.maps[record_id_str] = {}

        app.maps[record_id_str]['region_source'] = new VectorSource({
            features: []
        });

        app.maps[record_id_str]['region_layer'] = new VectorLayer({
            source: app.maps[record_id_str]['region_source'],
            style: app.regionSuggestionStyle,
        });



        app.maps[record_id_str]['map'] = new Map({
            target: 'record-map-' + record_suggestion_id,
            layers: [
                new TileLayer({
                    source: new OSM(),
                }),
                app.maps[record_id_str]['region_layer'],
            ],
            view: new View({
                center: [
                    -13803616.858365921,    // -124
                    4865942.279503175       // 40 
                ],
                zoom: 5,
            }),
        });

        app.maps[record_id_str]['region_source'].clear()
        
        let features = new GeoJSON().readFeatures(app.regions_loaded);
        // Flush any pre-existing features to clear out selection.
        if (app.maps[record_id_str]['region_source'].getFeatures.length < 1) {
            app.maps[record_id_str]['region_source'].addFeatures(features);
        }
        // app.recordMapLoadSelectedFeatures();
        app.mapZoomToBufferedExtent(app.maps[record_id_str]['region_source'].getExtent(), 0.1, app.maps[record_id_str]['map']);



    }
    
}