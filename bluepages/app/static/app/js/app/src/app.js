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

    $.post(submitAction, contact_form.serialize(), function(data){window.alert('Contact submitted!')});
}

app.suggestionModal = new Modal(document.getElementById('suggestionModal'), {});


$(document).ready( function () {
    $('#contact-results-table').DataTable();
} );