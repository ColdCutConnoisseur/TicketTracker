// Handles jQuery-based date/time pickers:

$(document).ready(function(){
    console.log("Datepicker script loaded");

    const dateEls = [//'#event-datepicker', '#date-purchased-datepicker'];
    for (let ind in dateEls) {
        $(dateEls[ind]).datepicker({
            format: 'mm/dd/yyyy',
            startDate: '-3d'
        });
    }

    const timeEls = [//'#event-timepicker'];
    for (let ind in timeEls) {
        $(timeEls[ind]).timepicker({
            showMeridian: false,
            minuteStep: 1
        });
    }
});