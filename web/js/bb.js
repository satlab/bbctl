var get_bbinfo = function ()
{
    $.ajax({
            url: '/bb/info',
        success: function(data) {
            $("#bbinfo").text(
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
                    // EPS
                    if (entry.beacon.eps) {
			            $("#valid-eps").removeClass().addClass("label label-success");
                        $("#bcn-eps-bootcount").text(entry.beacon.eps.bootcount);
                        $("#bcn-eps-bootcause").text(entry.beacon.eps.bootcause);
                        $("#bcn-eps-battvoltage").text(entry.beacon.eps.battvoltage);
                        $("#bcn-eps-battcurrent").text(entry.beacon.eps.battcurrent);
                        $("#bcn-eps-mainvoltage").text(entry.beacon.eps.mainvoltage);
                        $("#bcn-eps-temp-eps").text(entry.beacon.eps.temp_mean);
                        $("#bcn-eps-temp-pa").text(entry.beacon.eps.temp_pa);
                        $("#bcn-eps-uptime").text(entry.beacon.eps.uptime);
                    } else {
			            $("#valid-eps").removeClass().addClass("label label-default");
                        $("[id^=bcn-eps]").text("-");
                    }

                    // COM
                    if (entry.beacon.com) {
			            $("#valid-com").removeClass().addClass("label label-success");
                        $("#bcn-com-bootcount").text(entry.beacon.com.bootcount);
                        $("#bcn-com-bootcause").text(entry.beacon.com.bootcause);
                        $("#bcn-com-rx").text(entry.beacon.com.rx);
                        $("#bcn-com-tx").text(entry.beacon.com.tx);
                        $("#bcn-com-rssi").text(entry.beacon.com.last_rssi);
                        $("#bcn-com-fec").text(entry.beacon.com.last_bit_corr + "/" + entry.beacon.com.last_byte_corr);
                    } else {
			            $("#valid-com").removeClass().addClass("label label-default");
                        $("[id^=bcn-com]").text("-");
                    }

                    // ADCS1
                    if (entry.beacon.adcs1) {
			            $("#valid-adcs1").removeClass().addClass("label label-success");
                        $("#bcn-adcs1-bdot").text(entry.beacon.adcs1.bdot);
                        $("#bcn-adcs1-state").text(entry.beacon.adcs1.state);
                    } else {
			            $("#valid-adcs1").removeClass().addClass("label label-default");
                        $("[id^=bcn-adcs1]").text("-");
                    }

                    // ADCS2
                    if (entry.beacon.adcs2) {
			            $("#valid-adcs2").removeClass().addClass("label label-success");
                        $("#bcn-adcs2-gyro").text(entry.beacon.adcs2.gyro);
                    } else {
			            $("#valid-adcs2").removeClass().addClass("label label-default");
                        $("[id^=bcn-adcs2]").text("-");
                    }

                    // AIS
                    if (entry.beacon.ais2) {
			            $("#valid-ais").removeClass().addClass("label label-success");
                        $("#bcn-ais-bootcount").text(entry.beacon.ais2.bootcount);
                        $("#bcn-ais-crcok").text(entry.beacon.ais2.crc_ok);
                        $("#bcn-ais-lat").text(entry.beacon.ais2.latest_lat);
                        $("#bcn-ais-long").text(entry.beacon.ais2.latest_long);
                        $("#bcn-ais-mmsi").text(entry.beacon.ais2.latest_mmsi);
                        $("#bcn-ais-unique").text(entry.beacon.ais2.unique_mmsi);
                    } else {
			            $("#valid-ais").removeClass().addClass("label label-default");
                        $("[id^=bcn-ais]").text("-");

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
