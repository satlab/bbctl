#!/usr/bin/env python

# Copyright (c) 2016 Jeppe Ledet-Pedersen <jlp@satlab.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import codecs
import struct

class Beacon():
    BEACON_LENGTH = 84
    BEACON_DEST = 9
    BEACON_DPORT = 10

    # Data valid bits
    EPS_VALID = (1 << 0)
    COM_VALID = (1 << 1)
    ADCS1_VALID = (1 << 2)
    ADCS2_VALID = (1 << 3)
    AIS1_VALID = (1 << 4)
    AIS2_VALID = (1 << 5)

    def __init__(self, data):

        # Split into CSP header and beacon data
        hdata, bdata = data[:4], data[4:]
        header = struct.unpack("<I", hdata)[0]

        # Verify that destination is beacon receiver
        dst = (header >> 20) & 0x1f
        dport = (header >> 14) & 0x3f

        if dst != self.BEACON_DEST or dport != self.BEACON_DPORT:
            raise TypeError("Beacon destination does not match")

        if len(bdata) != self.BEACON_LENGTH:
            raise TypeError("Length does not match beacon")

        # Initialize beacon dictionary
        self.beacon = {}

        valid, eps, com, adcs1, adcs2, ais1, ais2 = struct.unpack("<B20s10s7s6s20s20s", bdata)

        if valid & self.EPS_VALID:
            """
            uint16_t eps_bootcount;     /* Boot counter. 3 MSB gives reset cause. Max boots 8191*/
            uint32_t eps_uptime;        /* Uptime, seconds */
            uint32_t eps_rtt;           /* Real-time Timer value, seconds */
            uint8_t eps_pingstatus;     /* Ping reply status */
            uint16_t eps_ss_status;     /* Power channel status, on/off */
            uint8_t eps_battvoltage;    /* Battery voltage, 0 = 0V, 255 = 10.2V+ (40mV resolution) */
            int8_t eps_celldiff;        /* Difference in battery cell voltage, 0 = 0V, 255 = 5V+ */
            int8_t eps_battcurrent;     /* Battery current, -128 = -1280 mA 0 = 0 mA, 127 = 1270 mA (10mA resolution)*/
            uint8_t eps_solarpower;     /* Solar panel power, 0 = mW, 255 = 5100 mW (20mW resolution)*/
            int8_t eps_temp_mean;       /* Mean temperature of the four temperatures on the EPS */
            int8_t eps_temp_pa;         /* Temperature of the PA */
            uint8_t eps_mainvoltage;    /* 0 = 0V, 255 = 5100 mV (20mV resolution) */
            """

            bootcount, uptime, rtt, pingstatus, ss_status, battvoltage, celldiff, battcurrent, solarpower, temp_mean, temp_pa, mainvoltage = struct.unpack(">HIIBHBbbBbbB", eps)

            self.beacon['eps'] = {
                'bootcount': bootcount & 0x1fff,
                'bootcause': bootcount >> 13,
                'uptime': uptime,
                'rtt': rtt,
                'pingstatus': pingstatus,
                'ss_status': ss_status,
                'battvoltage': battvoltage * 40,
                'celldiff': celldiff,
                'battcurrent': battcurrent * 10,
                'solarpower': solarpower * 20,
                'temp_mean': temp_mean,
                'temp_pa': temp_pa,
                'mainvoltage': mainvoltage * 20}


        if valid & self.COM_VALID:
            """
            uint16_t bootcount;         /* Boot counter */
            uint16_t packet_rx;         /* Packets received */
            uint16_t packet_tx;         /* Packets transmitted */
            int16_t  last_rssi;         /* RSSI of last received packet */
            uint8_t  last_bit_corr;     /* Bits corrected in last packet */
            uint8_t  last_byte_corr;    /* Bytes corrected in last packet */
            """
            bootcount, rx, tx, last_rssi, last_bit_corr, last_byte_corr = struct.unpack(">HHHhBB", com)

            self.beacon['com'] = {
                'bootcount': bootcount & 0x1fff,
                'bootcause': bootcount >> 13,
                'rx': rx,
                'tx': tx,
                'last_rssi': last_rssi,
                'last_bit_corr': last_bit_corr,
                'last_byte_corr': last_byte_corr}

        if valid & self.ADCS1_VALID:
            """
            int16_t bdot[3];            /* Bdot (gauss/sec * ConversionFactor) */
            int8_t state;               /* ADCS1 state */
            """
            bdot0, bdot1, bdot2, state = struct.unpack(">3hb", adcs1)
            bdot = (bdot0, bdot1, bdot2)
        
            self.beacon['adcs1'] = {
                'bdot': bdot,
                'state': state}

        if valid & self.ADCS2_VALID:
            """
            int16_t gyro_meas[3];       /* Gyro measurements (degrees per second * 100) */
            """
            gyro_meas = struct.unpack(">3h", adcs2)

            self.beacon['adcs2'] = {
                'gyro_meas':  gyro_meas}

        if valid & self.AIS2_VALID:
            """ 
            uint16_t bootcount;         /* Boot count */
            uint32_t crc_ok;            /* Packets with valid CRC16 */
            uint16_t unique_mmsi;       /* Unique MMSIs received */
            uint32_t latest_mmsi;       /* Newest MMSI */
            int32_t latest_long;        /* Longitude of newest message */
            int32_t latest_lat;         /* Latitude of newest message */
            """
            bootcount, crc_ok, unique_mmsi, latest_mmsi, latest_long, latest_lat = struct.unpack(">HIHIii", ais2)

            self.beacon['ais2'] = {
                'bootcount': bootcount, 
                'crc_ok': crc_ok,
                'unique_mmsi': unique_mmsi, 
                'latest_mmsi': latest_mmsi,
                'latest_long': latest_long, 
                'latest_lat': latest_lat}

    def fields(self):
        return self.beacon

def main():
    testdata = codecs.decode('00ac9248270018000006c2571b79517e0ed9c27310021c1da3000c0000003000000000ffb0003effce000000000000000000000000000000000000000000000000000000209a00001025000000000000000000000000000012ce', 'hex')
    
    # Drop 2 byte HMAC
    testdata = testdata[:-2]

    b = Beacon(testdata)
    import json
    print(json.dumps(b.fields(), sort_keys=True, indent=4))

if __name__ == '__main__':
    main()
