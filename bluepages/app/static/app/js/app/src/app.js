import { Modal } from 'bootstrap';
import * as $ from 'jquery';
import DataTable from 'datatables';
import Map from 'ol/Map';
import OSM from 'ol/source/OSM';
import VectorSource from 'ol/source/Vector';
import VectorLayer from 'ol/layer/Vector';
import TileLayer from 'ol/layer/Tile';
import View from 'ol/View';
import Style from 'ol/style/Style';
import Stroke from 'ol/style/Stroke';
import Fill from 'ol/style/Fill';
import Text from 'ol/style/Text';
import GeoJSON from 'ol/format/GeoJSON';

app.showAccountModal = function() {
    app.suggestionMenuModal.hide();
    app.exploreModal.hide();
    app.recordSuggestionModal.hide();
    app.suggestionModal.hide();
    app.accountModal.show();
}

app.showSuggestionMenuModal = function() {
    app.accountModal.hide();
    app.exploreModal.hide();
    app.recordSuggestionModal.hide();
    app.suggestionModal.hide();
    app.suggestionMenuModal.show();
}

app.showSuggestionFormModal = function() {
    app.accountModal.hide();
    app.exploreModal.hide();
    app.recordSuggestionModal.hide();
    app.suggestionMenuModal.hide();
    app.suggestionModal.show();
}

app.showRecordSuggestionFormModal = function() {
    app.accountModal.hide();
    app.exploreModal.hide();
    app.suggestionMenuModal.hide();
    app.suggestionModal.hide();
    app.recordSuggestionModal.show();
}

app.showExploreModal = function() {
    app.accountModal.hide();
    app.recordSuggestionModal.hide();
    app.suggestionMenuModal.hide();
    app.suggestionModal.hide();
    app.exploreModal.show();
}

app.checkRegistrationFormValidity = function() {
    if ($('#registration-form').checkValidity()) {
        $('#registration-form-submit').removeAttribute('disabled');
    } else {
        $('#registration-form-submit').setAttribute('disabled', 'disabled');
    }
}

app.loadRegistrationForm = function() {
    $.ajax({
        url: "/accounts/register/",
        success: function(registration_form) {
            $("#accountModalWrapper").html(registration_form);
            $("#registration-form").change(app.checkRegistrationFormValidity);
            app.showAccountModal();
        }
    });
}

app.submitRegistrationForm = function() {
    let registration_form = $("#registration-form");
    let submitAction = registration_form.attr('action');

    $.post(submitAction, registration_form.serialize(), app.handleRegistrationReturn)
}

app.handleRegistrationReturn = function(result) {
    if (result.indexOf('id="registration-form">') < 0) {
        $("#accountModalWrapper").html("Registration successful! You will now be logged in...");
        window.setTimeout(
            function() {
                window.location.assign('/');
            },
            1000
        );
    } else {
        $("#accountModalWrapper").html(result);
        app.showAccountModal();

    }
}

app.loadForgotCredentials = function() {
    $.ajax({
        url: "/accounts/forgot/",
        success: function(forgot_result) {
            $("#accountModalWrapper").html(forgot_result);
            // $("#registration-form").change(app.checkRegistrationFormValidity);
            app.showAccountModal();
        }
    });
}

app.submitPasswordReset = function() {
    let reset_form = $("#password-reset-form");
    let submitAction = reset_form.attr('action');

    $.post(submitAction, reset_form.serialize(), app.handlePasswordResetReturn)
}

app.handlePasswordResetReturn = function(result) {
    $("#accountModalWrapper").html(
        '<div class="content">' +
            '<div id="content" class="colM">' +
                '<h1>Password reset sent</h1>' +
                '<p>We’ve emailed you instructions for setting your password, if an account exists with the email you entered. You should receive them shortly.</p>' +
                '<p>If you don’t receive an email, please make sure you’ve entered the address you registered with, and check your spam folder.</p>' +
            '</div>' +
        '</div>'
    );
}

app.loadLoginForm = function() {
    $.ajax({
        url: "/accounts/login/",
        success: function(login_form) {
            $("#accountModalWrapper").html(login_form);
            app.showAccountModal();
        }
    });
}

app.handleLoginReturn = function(result) {
    if (result.indexOf('id="login-form">') < 0) {
        $("#accountModalWrapper").html("Login successful!");
        window.setTimeout(
            function() {
                window.location.assign('/');
            },
            1000
        );
    } else {
        $("#accountModalWrapper").html(result);
        app.showAccountModal();
    }
}

app.submitLoginForm = function() {
    let login_form = $("#login-form");
    let submitAction = login_form.attr('action');

    $.post(submitAction, login_form.serialize(), app.handleLoginReturn);
}

app.logoutRUS = function() {
    let html = "<div id='logout-rus'><p>Are you sure you wish to log out?</p><button class='btn btn-primary' data-bs-dismiss='modal'>Nevemind</button><a href='/accounts/logout/'><button class='btn btn-primary'>Yes, log me out</button></a></div>";
    $("#accountModalWrapper").html(html);
    app.showAccountModal();
}

app.loadAccountModal = function() {
    $.ajax({
        url: "/profile/",
        success: function(profile_modal) {
            $("#accountModalWrapper").html(profile_modal);
            app.showAccountModal();
        }
    })
}

app.loadProfileForm = function() {
    $.ajax({
        url: '/profile/edit/',
        success: function(profile_form) {
            $("#accountModalWrapper").html(profile_form);
            app.showAccountModal();
        }
    })
}

app.submitProfileForm = function() {
    let profile_form = $("#profile-form");
    let submitAction = profile_form.attr('action');

    $.post(submitAction, profile_form.serialize(), app.handleProfileReturn);
}

app.handleProfileReturn = function(result) {
    $("#accountModalWrapper").html(result);
    app.showAccountModal();
}

app.loadPasswordChangeForm = function() {
    $.ajax({
        url: '/profile/password_change/',
        success: function(password_form) {
            $("#accountModalWrapper").html(password_form);
            app.showAccountModal();
        }
    })
}

app.submitPasswordChangeForm = function() {
    let password_form = $("#password-form");
    let submitAction = password_form.attr('action');

    $.post(submitAction, password_form.serialize(), app.handlePasswordChangeReturn);
}

app.handlePasswordChangeReturn = function(result) {
    $("#accountModalWrapper").html(result);
    if (result.indexOf('<span id="password-reset-success"></span>') >= 0) {
        window.setTimeout(
            function() {
                window.location.assign('/');
            },
            3000
        );
    }

    app.showAccountModal();
}

app.loadSuggestionForm = function(contact_suggestion_id) {
    let url = "/suggestion_form/";
    if (contact_suggestion_id) {
        url = url + contact_suggestion_id + "/";
    }
    $.ajax({
        url: url,
        success: function(form){
            $("#suggestionModalWrapper").html(form);
            app.showSuggestionFormModal();
        }
    })
}

app.confirmSuggestionDeletion = function(contact_id) {
    if (window.confirm("Are you sure you wish to remove this suggestion? Please note that if this contact is in the database, only your suggestion will be removed; the contact will not be removed or changed.")) {
        $.ajax({
            url: "/delete_suggested_contact/" + contact_id + "/",
            success: window.setTimeout(app.loadSuggestionMenu, 200) 
        })
    }

}

app.submitContactSuggestion = function() {
    let contact_form = $("#contact-suggestion-form");
    let submitAction = contact_form .attr('action');

    // TODO: Validate form

    $.post(submitAction, contact_form.serialize(), app.prepContactMenuModal)
        .fail(function(error_form) {
            alert("error");
            $("#suggestionModalWrapper").html(error_form);
        });
}

app.loadSuggestionMenu = function() {
    $.ajax({
        url: "/get_suggestion_menu/",
        success: function(data) {
            if (typeof(data) == 'string') {
                $("#suggestionMenuModalWrapper").html(data)
                app.showSuggestionMenuModal();
            } else {
                // result not HTML, meaning no existing suggestion records were found
                app.loadSuggestionForm();
            }
        }
    })
}

app.prepContactMenuModal = function(data) {
    if (typeof(data) == 'string') {
        //Form contained an error and was returned to us
        $("#suggestionModalWrapper").html(data);
    } else {
        app.suggested_contact = data.contact_suggestion;
        $.ajax({
            url:"contact_suggestion_menu/" + data.contact_suggestion.id + "/",
            success: app.loadContactMenuModal
        })
    }
}

app.loadContactMenuModal = function(form_html) {
    $('#suggestionMenuModalWrapper').html(form_html);
    app.showSuggestionMenuModal();
}

app.prepRecordSuggestions = function(contact_id, record_id) {
    let url = "/record_suggestion_form/" + contact_id + "/";
    if (record_id){
        url += record_id + "/";
    }
    $.ajax({
        url: url,
        success: app.loadRecordSuggestionModal
    })
}

app.loadRecordSuggestionModal = function(data) {
    if (typeof(data) == 'string') {
        $('#recordSuggestionModalWrapper').html(data);
        $("#topicSuggestionContactName").html(app.suggested_contact.contact_name);
        app.loadRecordSuggestionForm();
        app.showRecordSuggestionFormModal();
    } else {
        app.suggested_contact = data.contact_suggestion;
        $.ajax({
            url:"contact_suggestion_menu/" + data.contact_suggestion.id + "/",
            success: app.loadContactMenuModal
        })
    }
    
}

app.prepExploreModal = function(key) {
    let url = "/explore/" + key.toLowerCase() + "/embedded/";
    $.ajax({
        url: url,
        success: app.loadExploreModal
    })
}

app.loadExploreModal = function(data) {
    $('#exploreModalWrapper').html(data);
    app.showExploreModal();
}

app.prepExploreDetailsModal = function(type, id) {
    let url = "/" + type + "/" + id + "/embedded/";
    app.exploreType = type;
    $.ajax({
        url: url,
        success: app.loadExploreDetailsModal
    })
}

app.loadExploreDetailsModal = function(data) {
    if (this.url.indexOf('entities') >= 0) {
        let back_button = '<div><button class="btn btn-primary detail-back-button" onclick="app.prepExploreModal(\'' + app.exploreType + '\')">&lt; Back </button></div>';
        $('#exploreModalWrapper').html(back_button + data);
    } else {
        $('#exploreModalWrapper').html(data);
    }
    app.showExploreModal();
}

app.toggleFilter = function(key) {
    app.updateState('open', key);
    let chevron = $("#filter-category-chevron-" + key);
    if (chevron.hasClass('bi-chevron-down')) {
        chevron.removeClass('bi-chevron-down');
        chevron.addClass('bi-chevron-right');
    } else {
        chevron.removeClass('bi-chevron-right');
        chevron.addClass('bi-chevron-down');
    }
}

app.loadSearchResults = function(results, status) {
    // pull filter/facets from data results to populate filters on left
    let filter_col_html = '';
    Object.keys(results.filters).forEach( key => {
        var is_expanded = app.filter_state['open'].indexOf(key) >= 0;
        filter_col_html += '<h2 class="filter-header">';
        if (is_expanded) {
            var chevron = '<i id="filter-category-chevron-' + key + '" class="bi bi-chevron-down filter-category-chevron"></i>';
            filter_col_html += '<span class="" ';
        } else {
            var chevron = '<i id="filter-category-chevron-' + key + '" class="bi bi-chevron-right filter-category-chevron"></i>';
            filter_col_html += '<span class="collapsed" ';
        }
        filter_col_html += 'data-bs-toggle="collapse" href="#' + key + 'FilterOptions" ' +
                    'aria-expanded="' + is_expanded + '" ' +
                    'aria-controls="collapse' + key + '" ' +
                    'onclick="app.toggleFilter(\'' + key + '\')">' +
                    chevron + 
                    key +
                '</span>';
        filter_col_html += '</h2>';
        if (is_expanded) {
            filter_col_html += '<ul class="collapse show" id="' + key +'FilterOptions">';
        } else {
            filter_col_html += '<ul class="collapse" id="' + key +'FilterOptions">';
        }
        results.filters[key].forEach( filter => {
            filter_col_html += '<li class="filter-list-item">' +
                    '<span type="' + key + '" value="' + filter.id + '" onclick="app.updateState(\'' + key.toLowerCase() + '\', \'' + filter.id + '\')">';
            if (app.filter_state[key.toLowerCase()].indexOf(filter.id) >= 0) {
                filter_col_html += '<b><i class="bi bi-check2-square"></i>' + filter.name  + '</b>';
            } else {
                filter_col_html += '<i class="bi bi-square"></i> ' + filter.name;
            }
            filter_col_html += '</span>' +
                '</li>';
        });
        filter_col_html += '</ul>' +
        '<br />';
    });
    $("#filter-column").html(filter_col_html);
        
    // (Re?)create DataTable, feeding in the 'contacts' results
    let results_col_html = '<button type="button" class="btn btn-primary export export-csv" onclick="app.exportToCSV()">' +
            'Export Data' +
        '</button>';
    results_col_html += '<table id="contact-results-table">' +
            '<thead>' +
                '<tr>' +
                    '<th>Name</th>' +
                    '<th>Role</th>' +
                    '<th>Entity</th>' +
                '</tr>' +
            '</thead>' +
            '<tbody>';
    results.contacts.forEach( contact => {
        results_col_html += '<tr id="contact-row-' + contact.id +'" class="contact-row ">' +
                '<td>' + contact.name + '</td>' +
                '<td>' + contact.role + '</td>' +
                '<td>' + contact.entity + '</td>' +
            '</tr>';
    })
    results_col_html += '</tbody>' +
        '</table>';
    $("#results-column div.contact-results").html(results_col_html);
    $('#contact-results-table').DataTable();
    $('#contact-results-table tbody').on('click', 'tr', function() {
        app.prepExploreDetailsModal('contacts', this.id.replace(/contact-row-/g, ''));
    })
    
}

app.updateState = function(filter, value) {
    if (!isNaN(parseInt(value))) {
        value = parseInt(value);
    }
    if (Object.keys(app.filter_state).indexOf(filter) < 0) {
        app.filter_state[filter] = [];
    }
    let val_index = app.filter_state[filter].indexOf(value)
    if (val_index >= 0) {
        app.filter_state[filter].splice(val_index, 1);
    } else {
        app.filter_state[filter].push(value);
    } 
    if (filter == 'regions') {
        app.mapUpdateFilters();
    } else if (filter != 'open') {
        app.getSearchResults();
    }
}

app.getMapLabel = function(feature) {
    let text = feature.get('name');
    return text;
}

app.mapStyleFunction = function(feature) {
    var label = app.getMapLabel(feature);
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

app.mapRegionSource = new VectorSource({
    features: []
});

app.mapVectorLayer = new VectorLayer({
    source: app.mapRegionSource,
    style: app.mapStyleFunction,
});

// Selection logic largely taken from OL examples:
//  https://openlayers.org/en/latest/examples/select-features.html
//  https://openlayers.org/en/latest/examples/select-multiple-features.html

app.mapSelectedStyleFunction = function(feature) {
    var label = app.getMapLabel(feature);
    let selectedStyle = new Style({
        fill: new Fill({
            color: 'rgba(255,255,255,0.1)'
        }),
        stroke: new Stroke({
            color: 'rgba(255,0,255,1.0)',
            width: 2,
        }),
        text: new Text({
            text: label,
            stroke: new Stroke({
                color: 'white',
                width: 1
            }),
            font: 'bold 12px sans-serif'
        })
    })
    return selectedStyle;
}

app.mapToggleFeatureSelection = function(feature, run_query)  {
    var sel_index = app.filter_state['map_regions'].indexOf(feature.get('id'));
    if ( sel_index < 0){
        feature.setStyle(app.mapSelectedStyleFunction(feature));
        app.filter_state['map_regions'].push(feature.get('id'));
    } else {
        feature.setStyle(undefined);
        app.filter_state['map_regions'].splice(sel_index, 1);
    }
    if (run_query) {
        app.getSearchResults();
    }
}

// Map and Form interactions:
app.mapUpdateFilters = function() {
    let regions = app.mapVectorLayer.getSource().getFeatures();
    let filtered_regions = [];
    let states = [];
    let depths = [];

    if (app.filter_state['regions'].indexOf('WA') >= 0) { states.push('WA')};
    if (app.filter_state['regions'].indexOf('OR') >= 0) { states.push('OR')};
    if (app.filter_state['regions'].indexOf('CA') >= 0) { states.push('CA')};

    if (app.filter_state['regions'].indexOf('OS') >= 0) { depths.push('O')};
    if (app.filter_state['regions'].indexOf('MD') >= 0) { depths.push('M')};
    if (app.filter_state['regions'].indexOf('NS') >= 0) { depths.push('N')};

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
        if (final_regions.indexOf(region) >= 0 && app.filter_state['map_regions'].indexOf(region.get('id')) < 0) {
            //select unselected region:
            app.mapToggleFeatureSelection(region, false);
        } else if (final_regions.indexOf(region) < 0 && app.filter_state['map_regions'].indexOf(region.get('id')) >= 0) {
            // unselect previously selected region:
            app.mapToggleFeatureSelection(region, false);
        }
    }
    app.getSearchResults();

}

// Load Regions onto map
app.mapZoomToBufferedExtent = function(extent, buffer) {
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
    app.map.getView().fit(buffered_extent, {'duration': 1000});
}

app.loadMapFilter = function(){
    // get map data
    $.ajax({
        url:'/static/app/data/regions.json',
        dataType: 'json'
    })
    .done(function(data) {
        window.setTimeout(
            function(){
                $("#map").html('');
                app.map = new Map({
                    layers: [
                        new TileLayer({
                            source: new OSM
                        }),
                        app.mapVectorLayer
                    ],
                    target: 'map',
                    view: new View({
                        center: [
                            -13803616.858365921,    // -124
                            4865942.279503175       // 40 
                        ],
                        zoom: 5,
                    })
                });
                
                app.mapRegionSource.clear();
                
                app.map.on('singleclick', function(e) {
                    app.map.forEachFeatureAtPixel(e.pixel, app.mapToggleFeatureSelection, true);
                });
                var features = new GeoJSON().readFeatures(data);
                // Flush any pre-existing features to clear out selection.
                if (app.mapRegionSource.getFeatures.length < 1) {
                    app.mapRegionSource.addFeatures(features);
                }

                app.mapZoomToBufferedExtent(app.mapRegionSource.getExtent(), 0.1);
            }, 150
        )
    });
}

app.getSearchResults = function() {
    // convert app.filter_state to AJAX query, then call app.loadSearchResults with the data
    $.ajax({
        url: "/filter_contacts",
        type: "POST",
        headers: {
            'X-CSRFToken': app.csrftoken
        },
        mode: 'same-origin',
        data: {'data': JSON.stringify(app.filter_state)},
        dataType: "json",
        success: app.loadSearchResults
    });
}


app.exportToCSV = function() {
    // let text_search_array = $("#contact-results-table_filter input").value.split(' ');
    // jquery with webpack is funky. Switching to vanilla JS for this:
    let text_search_array = document.getElementById("contact-results-table_filter").getElementsByTagName('input')[0].value.split(' ');
    let data = {
        'entities': app.filter_state['entities'],
        'topics': app.filter_state['topics'],
        'map_regions': app.filter_state['map_regions'],
        'text': text_search_array
    }
    $.ajax({
        url: "/export/csv/",
        type: "post",
        headers: {
            'X-CSRFToken': app.csrftoken
        },
        mode: 'same-origin',
        data: {'data': JSON.stringify(data)},
        // dataType: "text/csv",
        success: function(data) {
            let blob = new Blob([data]);
            let link = document.createElement('a');
            link.href=window.URL.createObjectURL(blob);
            link.download="bluepages_contacts.csv";
            link.click();
        }
    })
    .fail(function(){
        alert('Unable to export data.')
    });
}

app.accountModal = new Modal(document.getElementById('accountModal'), {});
app.suggestionMenuModal = new Modal(document.getElementById('suggestionMenuModal'), {});
app.suggestionModal = new Modal(document.getElementById('suggestionModal'), {});
app.exploreModal = new Modal(document.getElementById('exploreModal'), {});
app.recordSuggestionModal = new Modal(document.getElementById('recordSuggestionModal'), {});
app.filter_state = {
    'entities': [],
    'topics': [],
    'regions': [],
    'map_regions': [],              // Track which regions are selected on the map
    'open': []                      // Track whether left-panel filter categories are expanded or collapsed
};

$(document).ready( function () {
    app.loadMapFilter();
    app.getSearchResults();

} );