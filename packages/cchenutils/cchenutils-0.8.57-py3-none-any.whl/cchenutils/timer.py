import re
import time
from datetime import datetime

import dateutil.parser
import pytz
from dateutil.relativedelta import relativedelta


class Time:
    def now(self):
        return datetime.utcnow()

    @staticmethod
    def diff_in_seconds(a, b):
        d = a - b
        s = d.days * 3600 * 24 + d.seconds
        return abs(s)


class Timer(Time):
    def __init__(self):
        self.start_dt = self.now()
        self._last = self.start_dt

    def exec_from_start(self):
        self._last = self.now()
        return self.diff_in_seconds(self._last, self.start_dt)

    def exec_from_last(self):
        now = self.now()
        duration = self.diff_in_seconds(now, self._last)
        self._last = now
        return duration


class TimeController(Time):
    def __init__(self, mode, first_dt=None):
        self.mode = re.sub('^[0-9]*', '', mode)
        self.n = re.sub('[a-zA-Z]+$', '', mode)
        self.first_dt = first_dt if first_dt else self.now()

    def start(self):
        now = self.now()
        sleep = self.diff_in_seconds(now, self.first_dt if self.first_dt > now else self.next())
        print(f'Start in {self.beautify_time(sleep)}.')
        time.sleep(sleep + 1)
        self.start_dt = self.now()
        return self

    def restart(self, log=True):
        now = self.now()
        exec_time = self.diff_in_seconds(now, self.start_dt)
        sleep_time = self.diff_in_seconds(now, self.next()) + 1
        if log:
            print(f'\t{now.strftime("%Y-%m-%d %H:%M:%S")}, '
                  f'executed {self.beautify_time(exec_time)}: '
                  f'restart in {self.beautify_time(sleep_time)}'
                  , flush=True)
        time.sleep(sleep_time)
        self.start_dt = self.now()
        return self

    def next(self):
        fs = {'mo': 'months', 'w': 'weeks', 'd': 'days', 'h': 'hours', 'm': 'minutes'}
        _now = self.now()
        _next = self.first_dt
        while _next < _now:
            _next += relativedelta(**{fs[self.mode]: self.n})
        return _next

    def beautify_time(self, s):
        if self.mode == 'm':
            return f'{s}s'
        elif self.mode == 'h':
            return f'{s / 60:.2f}m'
        elif self.mode == 'd':
            return f'{s / 3600:.2f}h'
        else:
            return f'{s / 3600 / 24:.2f}d'

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if value not in (modes := ['mo', 'w', 'd', 'h', 'm']):
            raise ValueError(f'Mode must be in {", ".join(modes)}.')
        self._mode = value

    @property
    def n(self):
        return self._n

    @n.setter
    def n(self, value):
        self._n = int(value) if value else 1

    @property
    def first_dt(self):
        return self._first_dt

    @first_dt.setter
    def first_dt(self, value):
        self._first_dt = value if isinstance(value, datetime) else dateutil.parser.parse(value)
        if self._first_dt.tzinfo:
            self._first_dt = self._first_dt.astimezone(pytz.timezone('UTC')).replace(tzinfo=None)
