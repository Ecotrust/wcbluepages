import { Modal } from 'bootstrap';
import * as $ from 'jquery';
import DataTable from 'datatables';

app.loadSuggestionForm = function() {
    $.ajax({
        url: "/suggestion_form",
        success: function(form){
            $("#suggestionModalWrapper").html(form);
            app.suggestionModal.show();
        }
    })
}

app.submitContactSuggestion = function() {
    let contact_form = $("#contact-suggestion-form");
    let submitAction = contact_form .attr('action');

    // TODO: Validate form

    $.post(submitAction, contact_form.serialize(), app.prepRecordSuggestions)
        .fail(function(error_form) {
            alert("error");
            $("#suggestionModalWrapper").html(error_form);
        });
}

app.prepRecordSuggestions = function(data) {
    window.alert('Contact submitted!');
    app.suggested_contact = data.contact_suggestion;
    // load topic form
    $.ajax({
        url: "/record_suggestion_form/" + data.contact_suggestion.id + "/",
        success: app.loadRecordSuggestionModal
    })
}

app.loadRecordSuggestionModal = function(form_html) {
    app.suggestionModal.hide();
    $('#recordSuggestionModalWrapper').html(form_html);
    $("#topicSuggestionContactName").html(app.suggested_contact.contact_name);
    app.loadRecordSuggestionForm();
    app.recordSuggestionModal.show();
}

app.suggestionModal = new Modal(document.getElementById('suggestionModal'), {});
app.suggestionMenuModal = new Modal(document.getElementById('suggestionMenuModal'), {});
app.recordSuggestionModal = new Modal(document.getElementById('recordSuggestionModal'), {});


$(document).ready( function () {
    $('#contact-results-table').DataTable();
} );