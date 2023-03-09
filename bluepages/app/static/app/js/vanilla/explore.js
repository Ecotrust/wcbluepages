app.explore = {};

app.explore.toggleCollapseChevron = function(toggle_id) {
    console.log(toggle_id);
    let chevron = $("#explore-entity-chevron-" + toggle_id);
    let target = $("#explore-entity-children-" + toggle_id);
    if (chevron.hasClass('bi-chevron-right')) {
        chevron.removeClass('bi-chevron-right');
        chevron.addClass('bi-chevron-down');
    } else {
        chevron.removeClass('bi-chevron-down');
        chevron.addClass('bi-chevron-right');
    }
    target.collapse('toggle');
}