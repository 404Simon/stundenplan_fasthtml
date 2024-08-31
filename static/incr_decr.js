function modify_weeks_from_now(value) {
    var weeks = document.getElementById('weeks_from_now');
    if (weeks.value == "") {
        weeks.value = 0;
        weeks.blur();
    }
    weeks.value = parseInt(weeks.value) + value;
    weeks.dispatchEvent(new Event('change'));
}

function close_all_modals() {
    for (var i = 0; i < 5; i++) {
        var modal = document.getElementById('modal' + i);
        if (modal) {
            modal.close();
        }
    }
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
    } else if (e.key === "Escape" || e.key == "q") {
        close_all_modals();
    } else if (e.key >= '1' && e.key <= '5') {
        close_all_modals();
        var modal = document.getElementById('modal' + (parseInt(e.key) - 1));
        if (modal) {
            modal.showModal();
        }
    }
});
