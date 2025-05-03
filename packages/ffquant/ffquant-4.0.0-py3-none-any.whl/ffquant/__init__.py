from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .brokers import *
from .feeds import *
from .indicators import *
from .calendar import *
from .plot import *
from .utils import *

import requests
import time
import os
from ffquant.utils.Logger import stdout_log

# 备份原始的 requests.Session.request 方法
_original_request = requests.sessions.Session.request

# 自定义返回码
EXIT_CODE_NO_ROUTE = 100

def _patched_request(self, method, url, retries=3, delay=3, **kwargs):
    for attempt in range(retries):
        try:
            return _original_request(self, method, url, **kwargs)
        except OSError as e:
            if "No route to host" in str(e):
                stdout_log(f"[CRITICAL] request failed. url: {url}, method: {method}. ({attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    stdout_log(f"[FATAL] request failed after {retries} retries. url: {url}, method: {method}. Exiting process with code {EXIT_CODE_NO_ROUTE}.")
                    os._exit(EXIT_CODE_NO_ROUTE)  # 退出进程并返回特定的错误码
            else:
                raise

# 替换 requests.sessions.Session.request 方法
requests.sessions.Session.request = _patched_request