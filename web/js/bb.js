var get_rssi = function () {
    // request RSSI from bluebox
    $.ajax({
        url: '/bb/rssi',
        success: function(data) {
            $("#rssi").text(data.rssi + ' dBm');
        }
    });

    // rerun in 1000 ms
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
            $("#pass").text();
            $("#az").text(data.az.toFixed(2) + "\xB0");
            $("#el").text(data.elv.toFixed(2) + "\xB0");
            $("#slantrange").text((data.range/1000).toFixed(2) + " km");

            in_range = data.elv > 0;
            if (in_range) {
                text = "<span class=\"text-success\"><b>In-range</b></span> - pass ends in " + 
                    data.pass_ends;
            } else {
                text = "<span class=\"text-danger\"><b>Not in-range</b></span> - next pass in " + 
                    data.next_pass_in + " (" + 
                    data.next_pass_elv + "\xB0, " + 
                    data.next_pass_length + ")";
            }
            $("#pass").html(text)
        }
    });

    // rerun in 1000 ms
    setTimeout(get_tracking, 1000);
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
