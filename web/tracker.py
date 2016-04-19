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
import math
import datetime
import time

import ephem

class Tracker(threading.Thread):
    def __init__(self, bb, lat, lon, frequency, tle=None):
        # FIXME: add TLE downloader
        tle = [
            'GOMX 1                  ',
            '1 39430U 13066Q   16109.36557205  .00000570  00000-0  11404-3 0  9990',
            '2 39430  97.6740 134.8460 0151329 304.7268  53.9764 14.58545748128007']

        # Setup parameters
        self.bb = bb
        self.spacecraft = tle[0].strip()
        self.frequency = frequency

        # Setup observer
        self.obs = ephem.Observer()
        self.obs.lat = '{}'.format(lat)
        self.obs.long = '{}'.format(lon)

        # Setup spacecraft
        self.sc = ephem.readtle(tle[0], tle[1], tle[2])

        # Start thread
        threading.Thread.__init__(self, None)
        self.start()

    def pass_info(self):
        delta_start = ephem.localtime(self.tr) - datetime.datetime.now()
        delta_end = ephem.localtime(self.ts) - datetime.datetime.now()
        max_alt = math.degrees(self.altt)

        return {'spacecraft': self.spacecraft,
                'frequency': self.current_freq,
                'az': round(math.degrees(self.sc.az), 2),
                'elv': round(math.degrees(self.sc.alt), 2),
                'range': self.sc.range,
                'range_velocity': self.sc.range_velocity,
                'pass_ends': str(datetime.timedelta(delta_end.days, delta_end.seconds)),
                'next_pass_in': str(datetime.timedelta(delta_start.days, delta_start.seconds)),
                'next_pass_length': str(ephem.localtime(self.ts) - ephem.localtime(self.tr)),
                'next_pass_elv': round(max_alt, 2)}

    def doppler_shift(self, frequency, velocity):
        c = 299792458.0
        return (-velocity * frequency) / c

    def run(self):
        while True:
            # Find next pass
            self.obs.date = ephem.now()
            self.tr, self.azr, self.tt, self.altt, self.ts, self.azs = self.obs.next_pass(self.sc)

            # Handle pass
            self.obs.date = ephem.now()
            while self.obs.date <= self.ts:
                # Calculate spacecraft position
                self.sc.compute(self.obs)

                # Adjust radio frequency
                self.current_freq = self.frequency
                if self.sc.alt >= 0.0:
                    self.current_freq += self.doppler_shift(self.frequency, self.sc.range_velocity)
                self.bb.set_frequency(int(self.current_freq))

                # Wait for next update
                self.obs.date = ephem.Date(self.obs.date + 2 * ephem.second)
                time.sleep(2)
