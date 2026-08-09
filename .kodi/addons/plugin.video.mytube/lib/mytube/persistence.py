# -*- coding: utf-8 -*-


from collections import OrderedDict

from nuttig import save, Persistent


# ------------------------------------------------------------------------------
# MyNavigationHistory

class MyNavigationHistory(Persistent, dict):

    def __missing__(self, action):
        self[action] = list()
        return self[action]

    def __push__(self, action, key, value):
        if ((item := {key: value}) in self[action]):
            self[action] = self[action][:self[action].index(item)]
        try:
            return self[action][-1]
        except IndexError:
            return None
        finally:
            self[action].append(item)

    @save
    def page(self, action, page):
        if (page == 1):
            self[action].clear()
        return self.__push__(action, "page", page)

    @save
    def continuation(self, action, continuation):
        if (not continuation):
            self[action].clear()
        return self.__push__(action, "continuation", continuation)

    @save
    def clear(self):
        super(MyNavigationHistory, self).clear()


# ------------------------------------------------------------------------------
# MySearchHistory

class MySearchHistory(Persistent, OrderedDict):

    @save
    def record(self, query):
        self[(q := query["query"])] = query
        super(MySearchHistory, self).move_to_end(q)

    @save
    def remove(self, q):
        del self[q]

    @save
    def clear(self):
        super(MySearchHistory, self).clear()

    @save
    def move_to_end(self, q):
        super(MySearchHistory, self).move_to_end(q)


# ------------------------------------------------------------------------------
# MyFeedChannels

class MyFeedChannels(Persistent, OrderedDict):

    @save
    def add(self, key, value):
        self[key] = value

    @save
    def remove(self, key):
        del self[key]

    @save
    def clear(self):
        super(MyFeedChannels, self).clear()
