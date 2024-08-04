function modify_weeks_from_now(value) {
    var weeks = document.getElementById('weeks_from_now');
    if (weeks.value == "") {
        weeks.value = 0;
        weeks.blur();
    }
    weeks.value = parseInt(weeks.value) + value;
    weeks.dispatchEvent(new Event('change'));
}

document.addEventListener('keydown', function(e) {
    if (e.key === 'k' || e.key === 'ArrowLeft') {
        modify_weeks_from_now(-1);
    } else if (e.key === 'j' || e.key === 'ArrowRight') {
        modify_weeks_from_now(1);
    } else if (e.key === ":") {
        var weeks = document.getElementById('weeks_from_now');
        weeks.focus();
        weeks.select();
    }
});