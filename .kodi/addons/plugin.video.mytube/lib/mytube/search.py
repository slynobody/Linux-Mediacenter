# -*- coding: utf-8 -*-


from collections import deque, OrderedDict

from iapc import public
from nuttig import (
    containerRefresh, getSetting, inputDialog, localizedString,
    notify, selectDialog, ICONINFO
)

from mytube.extract import traverse, MyResults
from mytube.persistence import MySearchHistory
from mytube.utils import confirm


#-------------------------------------------------------------------------------

queryType = OrderedDict(
    (
        (None, {"label": 42230, "params": None}),
        ("all", {"label": 42211, "params": "="}),
        ("video", {"label": 42212, "params": "SAhAB"}),
        ("channel", {"label": 42213, "params": "SAhAC"}),
        ("playlist", {"label": 42214, "params": "SAhAD"})
    )
)


querySort = OrderedDict(
    (
        (None, {"label": 42230, "params": None}),
        ("relevance", {"label": 42221, "params": "CAA"}),
        ("upload_date", {"label": 42222, "params": "CAI"}),
        ("view_count", {"label": 42223, "params": "CAM"}),
        ("rating", {"label": 42224, "params": "CAE"})
    )
)


__queryParams__ = {
    qtk: {
        qsk: f"{qsv['params']}{qtv['params']}"
        for qsk, qsv in querySort.items() if qsk
    }
    for qtk, qtv in queryType.items() if qtk
}


#-------------------------------------------------------------------------------
# MySearch

class MySearch(object):

    def __init__(self, logger, session):
        self.logger = logger.getLogger(component="search")
        self.__session__ = session
        self.__queries__ = MySearchHistory()
        self.__cache__ = deque()

    def __q_setup__(self, setting, ordered, label):
        q_setting = list(ordered.keys())[getSetting(*setting)]
        self.logger.info(
            f"{localizedString(label)}: "
            f"{localizedString(ordered[q_setting]['label'])}"
        )
        return q_setting

    def __setup__(self):
        if (
            (not (history := getSetting("search.history", bool))) and
            self.__queries__
        ):
            self.__queries__.clear()
            notify(localizedString(90003), icon=ICONINFO, time=1000)
        self.__history__ = history
        self.logger.info(f"{localizedString(42110)}: {self.__history__}")
        self.__q_type__ = self.__q_setup__(
            ("query.type", int), queryType, 42210
        )
        self.__q_sort__ = self.__q_setup__(
            ("query.sort", int), querySort, 42220
        )

    def __stop__(self):
        self.__session__ = None
        self.logger.info("stopped")

    # query --------------------------------------------------------------------

    def __q_select__(self, key, ordered, heading):
        keys = [key for key in ordered.keys() if key]
        index = selectDialog(
            [localizedString(ordered[key]["label"]) for key in keys],
            heading=heading,
            preselect=keys.index(key)
        )
        return key if index < 0 else keys[index]

    def q_type(self, type="all"):
        return self.__q_select__(type, queryType, 42210)

    def q_sort(self, sort="relevance"):
        return self.__q_select__(sort, querySort, 42220)

    @public
    def query(self, **query): # this is a trick!
        # that method doesn't take keyword arguments
        try:
            query = self.__cache__.pop()
        except IndexError:
            if (q := inputDialog(heading=137)):
                query = {
                    "query": q,
                    "type": self.__q_type__ or self.q_type(),
                    "sort": self.__q_sort__ or self.q_sort()
                }
                if self.__history__:
                    self.__queries__.record(query)
        return query

    # history ------------------------------------------------------------------

    @public
    def history(self):
        self.__cache__.clear()
        return list(reversed(self.__queries__.values()))

    # search -------------------------------------------------------------------

    def __continue__(self, continuation):
        return self.__session__.__continue__(
            "search", continuation, "onResponseReceivedCommands"
        )

    def __start_search__(self, **kwargs):
        return traverse(
            self.__session__.__search__(**kwargs),
            "contents",
            "twoColumnSearchResultsRenderer",
            "primaryContents",
            "sectionListRenderer",
            "contents",
            default=[]
        )

    def __skip__(self, results):
        data = traverse(
            results, 0, "itemSectionRenderer", "contents", default=[]
        )
        #self.logger.info(f"len(data): {len(data)}")
        #self.logger.info(f"{data[0].get('adSlotRenderer')}")
        return ((len(data) == 1) and data[0].get("adSlotRenderer"))

    def __search__(self, **kwargs):
        results = {}
        if (continuation := kwargs.pop("continuation", None)):
            results = self.__continue__(continuation)
        elif "query" in kwargs:
            while (
                (results := self.__start_search__(**kwargs)) and
                self.__skip__(results)
            ):
                self.logger.info("skipping results")
        return MyResults(results)

    @public
    def search(self, **query):
        self.__cache__.append(query)
        if self.__history__:
            self.__queries__.move_to_end(query["query"])
        return self.__search__(
            query=query["query"],
            continuation=query.get("continuation"),
            params=__queryParams__[query["type"]][query["sort"]]
        )

    # --------------------------------------------------------------------------

    @public
    def updateQueryType(self, q):
        _query_ = self.__queries__[q]
        _type_ = _query_["type"]
        if ((type := self.q_type(type=_type_)) != _type_):
            _query_["type"] = type
            self.__queries__.record(_query_)
            containerRefresh()

    @public
    def updateQuerySort(self, q):
        _query_ = self.__queries__[q]
        _sort_ = _query_["sort"]
        if ((sort := self.q_sort(sort=_sort_)) != _sort_):
            _query_["sort"] = sort
            self.__queries__.record(_query_)
            containerRefresh()

    @public
    def removeQuery(self, q):
        self.__queries__.remove(q)
        containerRefresh()

    @public
    def clearHistory(self):
        if confirm():
            self.__queries__.clear()
            containerRefresh()
