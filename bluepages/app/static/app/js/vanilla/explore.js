app.explore = {};

app.explore.toggleCollapseChevron = function(toggle_id) {
    console.log(toggle_id);
    let chevron = $("#explore-entity-chevron-" + toggle_id);
    let target = $("#explore-entity-children-" + toggle_id);
    if (chevron.hasClass('bi-chevron-down')) {
        chevron.removeClass('bi-chevron-down');
        chevron.addClass('bi-chevron-up');
    } else {
        chevron.removeClass('bi-chevron-up');
        chevron.addClass('bi-chevron-down');
    }
    target.collapse('toggle');
}