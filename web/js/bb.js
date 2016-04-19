var get_bbinfo = function ()
{
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

var get_tracking = function ()
{
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

    setTimeout(get_tracking, 1000);
}

next_packet = 0;
var get_packets = function ()
{
    $.ajax({
        url: '/packets/' + next_packet,
        success: function(data) {
            data.packets.forEach(function(entry) {
                $("#wait-data").hide();
                if (entry.beacon) {
                    type = "Beacon";
                } else {
                    type = "Command";
                }
                $("#packets tbody").prepend($(
                    "<tr>" +
                        "<td>" + entry.count + "</td>" +
                        "<td>" + entry.time + "</td>" +
                        "<td>" + entry.rssi + " dBm</td>" +
                        "<td>" + entry.freq + " Hz</td>" +
                        "<td>" + entry.bitcorr + "/" + entry.bytecorr + "</td>" +
                        "<td>" + entry.datalen + "</td>" +
                        "<td>" + type + "</td>" +
                    "</tr>").hide().fadeIn(500));

                // parse beacon
                if (entry.beacon) {
                    if (entry.beacon.eps) {

                    }
                    if (entry.beacon.com) {

                    }
                }

                next_packet = entry.count + 1;
            });
        }
    });

    setTimeout(get_packets, 250);
}

var main = function ()
{
    // get bluebox info
    get_bbinfo();

    // start tracking update
    get_tracking();

    // start data update
    get_packets();
}

$(document).ready(main);
