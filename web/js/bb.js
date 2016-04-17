var get_rssi = function () {
    // request RSSI from bluebox
    $.ajax({
        url: '/bb/rssi',
        success: function(data) {
            $("#rssi").text(data.rssi + ' dBm');
        }
    });

    // rerun in 250 ms
    setTimeout(get_rssi, 1000);
}

var get_bbinfo = function () {
    // request info from bluebox
    $.ajax({
            url: '/bb/info',
        success: function(data) {
            $("#bbinfo").text(
                "Connected to " +
                data.manufacturer + " " +
                data.product + " (#" +
                data.serial + "/" +
                data.fwrevision + ")");
        }
    });
}

var get_tracking = function () {
    // request RSSI from bluebox
    $.ajax({
        url: '/tracker',
        success: function(data) {
            $("#spacecraft").text(data.spacecraft);
            $("#freq").text((data.frequency/1e6).toFixed(6) + " MHz");
            $("#pass").text(data.next_pass_in + " (" + data.next_pass_elv + "\xB0, " + data.next_pass_length + ")");
            $("#az").text(data.az + "\xB0");
            $("#el").text(data.elv + "\xB0");
            $("#slantrange").text(data.range/1000 + " km");

            in_range = data.elv > 0;
            if (in_range) {
                $("#inrange").text("Yes").removeClass().addClass("text-success");
            } else {
                $("#inrange").text("No").removeClass().addClass("text-danger");
            }
        }
    });

    // rerun in 250 ms
    setTimeout(get_tracking, 500);
}

var main = function () {
    // get info
    get_bbinfo();

    // start tracking update
    get_tracking();

    // start RSSI update
    get_rssi();
}

$(document).ready(main);
