import { Modal } from 'bootstrap';
import * as $ from 'jquery';
import DataTable from 'datatables';

app.loadSuggestionForm = function(contact_suggestion_id) {
    let url = "/suggestion_form/";
    if (contact_suggestion_id) {
        url = url + contact_suggestion_id + "/";
    }
    $.ajax({
        url: url,
        success: function(form){
            $("#suggestionModalWrapper").html(form);
            app.recordSuggestionModal.hide();
            app.suggestionMenuModal.hide();
            app.suggestionModal.show();
        }
    })
}

app.confirmSuggestionDeletion = function(contact_id) {
    if (window.confirm("Are you sure you wish to delete this suggestion?")) {
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
    // app.suggestionMenuModal.hide();
    // $("#suggestionMenuModalWrapper").html('')
    $.ajax({
        url: "/get_suggestion_menu/",
        success: function(data) {
            if (typeof(data) == 'string') {
                $("#suggestionMenuModalWrapper").html(data)
                app.suggestionModal.hide();
                app.recordSuggestionModal.hide();
                app.suggestionMenuModal.show();
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
    app.suggestionModal.hide();
    app.recordSuggestionModal.hide();
    app.suggestionMenuModal.show();
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

app.loadRecordSuggestionModal = function(form_html) {
    app.suggestionModal.hide();
    app.suggestionMenuModal.hide();
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