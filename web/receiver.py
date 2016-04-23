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

import threading
import time
import codecs
import datetime
import json

from fec import PacketHandler
from beacon import Beacon

class Receiver(threading.Thread):
    def __init__(self, bb, packetlog):
        # Setup parameters
        self.bb = bb
        self.packetlog = open(packetlog, 'a')

        # Packet list
        self._packets = []

        # Start thread
        threading.Thread.__init__(self, None)
        self.start()

    def run(self):
        count = 0
        ph = PacketHandler()

        while True:
            bit_corr = 0
            byte_corr = 0
            data, rssi, freq = self.bb.receive(100)
            if data is None:
                continue

            try:
                data, bit_corr, byte_corr = ph.deframe(data)
            except:
                continue

            print("{0:03} {1:.2f} RX ({2:03d}/{3:03d}) {4:4} dBm {5:+5d} Hz ({6:03}) '{7}'".format(
                count, time.time(), bit_corr, byte_corr, rssi, freq, len(data), codecs.encode(data, "hex")))

            packet = {
                'count': count,
                'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'rssi': rssi,
                'freq': freq,
                'bitcorr': bit_corr,
                'bytecorr': byte_corr,
                #'data': codecs.encode(data, "hex"),
                'datalen': len(data)
            }

            # Try to parse as beacon
            try:
                # Drop 2 byte HMAC
                bcn = Beacon(data[:-2])
                packet['beacon'] = bcn.fields()
            except Exception as e:
                pass
    
            print(json.dumps(packet, sort_keys=True, indent=4))

            # Append to packet list
            self._packets.append(packet)
            count += 1

    def packets(self, start):
        # return packets from next, up to the last 10
        return self._packets[start:][-10:]
