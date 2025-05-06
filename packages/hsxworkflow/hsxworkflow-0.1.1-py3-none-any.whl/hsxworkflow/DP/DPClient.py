import time

from DrissionPage import Chromium, ChromiumOptions

auto_port = True

baseConfig = ChromiumOptions()
if auto_port:
    baseConfig.auto_port()


class DriverClient:

    def __init__(self):
        self.__browser = None
        self.driver_tab = {}
        self.clear_query = {"cookies": True, "cache": True, "session_storage": True, "local_storage": True}

    def get_browser(self, latest_tab: bool = True, new_tab: bool = False) -> Chromium:
        if not self.__browser:
            raise Exception("Browser not initialized,Please first init Browser [init_driver]")
        if new_tab:
            self.__browser.new_tab()
            return self.__browser.latest_tab

        return self.__browser if latest_tab is False else self.__browser.latest_tab

    def init_driver(self, new_env: bool = True):
        if new_env:
            baseConfig.new_env()
        self.__browser = Chromium(baseConfig)

    def close_page(self, tabs_range: tuple = None, remainder_one: bool = True, clear_: bool = True,
                   close_interval: int = 0, *args, **kwargs):
        if not self.__browser:
            raise Exception("Browser not initialized,Please first init Browser [init_driver]")

        tab_list = self.__browser.get_tabs()
        if tabs_range:
            tab_list = tab_list[tabs_range[0]:tabs_range[1]]

        # tab_list.reverse()
        tab_count = len(tab_list)
        for i, tab in enumerate(tab_list):
            if i + 1 == tab_count and remainder_one:
                continue
            if clear_:
                for key in kwargs.keys():
                    if key in self.clear_query:
                        self.clear_query[key] = kwargs[key]
                tab.clear_cache(**self.clear_query)
            self.__browser.close_tabs(tab)

            time.sleep(close_interval)
