# frustratingly familiar favicon fetcher for FlowLauncher
# Fetches favicons using Google's favicon service

import sys
from pathlib import Path

from rfc3986 import is_valid_uri

plugindir = Path.absolute(Path(__file__).parent)
paths = (".", "lib", "plugin")
sys.path = [str(plugindir / p) for p in paths] + sys.path

import os
import requests
import base64
import re

from pyflowlauncher import Plugin, Result, send_results
from pyflowlauncher.result import ResultResponse
from pyflowlauncher.icons import (
    OK,
    CANCEL,
    WARNING,
    FIND,
    SETTINGS,
    UPDATE,
    CHECKUPDATE,
)
from pyflowlauncher import api


plugin = Plugin()

GOOGLE_FAVICON_URL = "https://www.google.com/s2/favicons?sz=256&domain="

@plugin.on_method
def query(query: str) -> ResultResponse:
    # For starters, we'll only send a request for valid URLs
    if not is_valid_uri(query):
        return send_results(
            [
                Result(
                    Title="Please enter a URL",
                    SubTitle="Enter a URL to fetch its favicon",
                    IcoPath=CANCEL,
                    RoundedIcon=True,
                )
            ]
        )
    else:
        return send_results(
            [
                Result(
                    Title="Is valid URL",
                    SubTitle="I hope so",
                    IcoPath=OK,
                    RoundedIcon=True,
                )
            ]
        )


plugin.run()
