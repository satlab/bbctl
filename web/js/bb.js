var get_rssi = function () {
    // request RSSI from bluebox
    $.ajax({
        url: '/rssi',
        success: function(data) {
            $("#rssi").text(data.rssi + ' dBm');
        }
    });

    // rerun in 250 ms
    setTimeout(get_rssi, 250);
}

var main = function () {
    // start RSSO update
    get_rssi();
}

$(document).ready(main);
