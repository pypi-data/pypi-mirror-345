from .timer import Timer


class Monitor:
    def __init__(self, mode, offset, timezone='UTC', exclude=None, notifier=None):
        self.exclude = set() if exclude is None else exclude
        self.timer = Timer(timezone)
        self.timer.restart(mode, offset=offset)
        self.mode = mode
        self.offset = offset
        self.notifier = notifier


    # def start(self, func, iterable):
    #     now = self.timer.start.strftime('%Y-%m-%d %H:%M:%S %Z')
    #     while True:
    #         for item in iterable:
    #             if item not in self.exclude:
    #                 res = func(item)
    #
    #
    #         if (msg := self.function()):
    #             self.notify(msg)
    #         self.timer.restart(self.mode, offset=self.offset)

    def notify(self, body):
        self.notifier.send(body)
        return self

    @property
    def notifier(self):
        return self._notifier

    @notifier.setter
    def notifier(self, value):
        self._notifier = value

    def __enter__(self):
        return self

    def __exit__(self, **kwargs):
        self.notifier.__exit__(**kwargs)
