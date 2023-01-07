import { Modal } from 'bootstrap';
import * as $ from 'jquery';
import DataTable from 'datatables';

app.showAccountModal = function() {
    app.suggestionMenuModal.hide();
    app.suggestionModal.hide();
    app.recordSuggestionModal.hide();
    app.accountModal.show();
}

app.showSuggestionMenuModal = function() {
    app.accountModal.hide();
    app.suggestionModal.hide();
    app.recordSuggestionModal.hide();
    app.suggestionMenuModal.show();
}

app.showSuggestionFormModal = function() {
    app.accountModal.hide();
    app.suggestionMenuModal.hide();
    app.recordSuggestionModal.hide();
    app.suggestionModal.show();
}

app.showRecordSuggestionFormModal = function() {
    app.accountModal.hide();
    app.suggestionMenuModal.hide();
    app.suggestionModal.hide();
    app.recordSuggestionModal.show();
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
                window.location.reload();
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
                window.location.reload();
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
                window.location.reload();
            },
            2200
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

app.accountModal = new Modal(document.getElementById('accountModal'), {});
app.suggestionMenuModal = new Modal(document.getElementById('suggestionMenuModal'), {});
app.suggestionModal = new Modal(document.getElementById('suggestionModal'), {});
app.recordSuggestionModal = new Modal(document.getElementById('recordSuggestionModal'), {});


$(document).ready( function () {
    $('#contact-results-table').DataTable();
} );