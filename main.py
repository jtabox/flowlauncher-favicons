# frustratingly familiar favicon fetcher for FlowLauncher
# Fetches favicons using Google's favicon service

import sys
from pathlib import Path

plugindir = Path.absolute(Path(__file__).parent)
paths = (".", "lib", "plugin")
sys.path = [str(plugindir / p) for p in paths] + sys.path

import requests
import base64
import re
from time import sleep

from pyflowlauncher import Plugin, Result, send_results
from pyflowlauncher.result import ResultResponse
from pyflowlauncher import api


plugin = Plugin()

GOOGLE_FAVICON_URL = "https://www.google.com/s2/favicons?sz=256&domain="


@plugin.on_method
def query(query: str) -> ResultResponse:
    # This is called whenever the text in the search box changes.
    # So we can implement a time delay to avoid sending requests for every keystroke.
    sleep(0.5)
    results_list = []
    # Check for valid domain (the query can never be empty, since otherwise this wouldn't be running)
    query = query.strip()
    if not is_valid_domain(query):
        results_list.append(
            Result(
                Title="Please enter a URL or a domain to fetch its favicon",
                SubTitle="Do NOT include http:// or https:// or other protocols",
                IcoPath="images\\05.png",
                RoundedIcon=True,
            )
        )
    else:
        try:
            response = requests.get(GOOGLE_FAVICON_URL + query, timeout=5)
            response.raise_for_status()  # Raise an error for bad responses
            favicon_data = base64.b64encode(response.content).decode("utf-8")

            results_list.append(
                Result(
                    Title=f"Found and fetched favicon for {query} successfully - Choose an action",
                    IcoPath=f"{GOOGLE_FAVICON_URL + query}",
                    RoundedIcon=True,
                    Score=100,
                )
            )
            results_list.append(
                Result(
                    Title="Copy favicon URL",
                    SubTitle=f"[{GOOGLE_FAVICON_URL + query}]",
                    IcoPath="images\\02.png",
                    RoundedIcon=True,
                    JsonRPCAction=api.copy_to_clipboard(
                        str(GOOGLE_FAVICON_URL + query), show_default_notification=False
                    ),
                    Score=90,
                )
            )
            results_list.append(
                Result(
                    Title="Copy base64 data URI",
                    SubTitle='Use in an <img src="data:..."> or directly in the browser address bar',
                    IcoPath="images\\03.png",
                    RoundedIcon=True,
                    JsonRPCAction=api.copy_to_clipboard(
                        f"data:image/png;base64,{favicon_data}",
                        show_default_notification=False,
                    ),
                    Score=80,
                )
            )
            results_list.append(
                Result(
                    Title="Copy only base64",
                    IcoPath="images\\04.png",
                    RoundedIcon=True,
                    JsonRPCAction=api.copy_to_clipboard(
                        favicon_data, show_default_notification=False
                    ),
                    Score=70,
                )
            )
        except requests.RequestException as e:
            results_list.append(
                Result(
                    Title="Error fetching favicon",
                    SubTitle=str(e),
                    IcoPath="images\\06.png",
                    RoundedIcon=True,
                )
            )

    # Send the results back to Flow Launcher
    return send_results(results_list)


@plugin.on_method
def is_valid_domain(query: str) -> bool:
    # A very basic regex to check if the query is a valid domain, where valid domain is essentially:
    # xxx.yy (at least 3 of [a-zA-Z0-9\-] followed by a dot and at least 2 of [a-zA-Z] - i don't think
    # domain codes include numbers or dashes). and also xxx doesn't start with a digit or starts/ends with a dash or a dot.
    pattern = r"^(?![-.\d])[a-zA-Z0-9-.]{3,}(?<![-.])\.[a-zA-Z]{2,}$"
    return re.match(pattern, query) is not None


plugin.run()
