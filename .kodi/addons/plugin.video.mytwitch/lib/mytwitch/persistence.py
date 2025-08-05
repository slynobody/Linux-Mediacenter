# -*- coding: utf-8 -*-


from collections import OrderedDict

from nuttig import save, Persistent


# ------------------------------------------------------------------------------
# MyChannels

class MyChannels(Persistent, OrderedDict):

    @save
    def add(self, name):
        self[channel] = {"channel": (channel := name.lower()), "name": name}
        super(MyChannels, self).move_to_end(channel)

    @save
    def remove(self, channel):
        del self[channel]

    @save
    def rename(self, channel, name):
        self[channel]["name"] = name

    @save
    def clear(self):
        super(MyChannels, self).clear()

    @save
    def move_to_end(self, channel):
        super(MyChannels, self).move_to_end(channel)
