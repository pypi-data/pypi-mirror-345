# https://docs.searxng.org/dev/search_api.html


from pprint import pprint
import requests
from typing import Optional, List, Literal
from dotenv import load_dotenv
import os

class SearXNG:
    def __init__(self, base_url:str=""):
        load_dotenv()
        base_url = os.getenv("SEARXNG_BASE_URL")
        self.base_url = base_url.rstrip("/") + "/search"

    def search(
        self,
        query: str,
        categories: Optional[
            Literal[
                "general", "images", "news", "it", "science",
                "videos", "music", "social media", "files", "map"
            ]
        ] = None,
        engines: Optional[str] = None,
        language: Optional[str] = None,
        pageno: int = 1,
        time_range: Optional[Literal["day", "month", "year"]] = None,
        format: Optional[Literal["json", "csv", "rss"]] = "json",
        results_on_new_tab: int = 0,
        image_proxy: Optional[bool] = None,
        autocomplete: Optional[
            Literal[
                "google", "dbpedia", "duckduckgo", "mwmb1", "startpage",
                "wikipedia", "stract", "swisscows", "qwant"
            ]
        ] = None,
        safesearch: Optional[Literal[0, 1, 2]] = None,
        theme: Optional[str] = "simple",
        enabled_plugins: Optional[List[str]] = None,
        disabled_plugins: Optional[List[str]] = None,
        enabled_engines: Optional[List[str]] = None,
        disabled_engines: Optional[List[str]] = None,
    ) -> dict:
        params = {
            "q": query,
            "pageno": pageno,
            "format": format,
            "results_on_new_tab": results_on_new_tab,
            "theme": theme,
        }

        if categories:
            params["categories"] = categories
        if engines:
            params["engines"] = engines
        if language:
            params["language"] = language
        if time_range:
            params["time_range"] = time_range
        if image_proxy is not None:
            params["image_proxy"] = str(image_proxy).lower()
        if autocomplete:
            params["autocomplete"] = autocomplete
        if safesearch is not None:
            params["safesearch"] = safesearch
        if enabled_plugins:
            params["enabled_plugins"] = ",".join(enabled_plugins)
        if disabled_plugins:
            params["disabled_plugins"] = ",".join(disabled_plugins)
        if enabled_engines:
            params["enabled_engines"] = ",".join(enabled_engines)
        if disabled_engines:
            params["disabled_engines"] = ",".join(disabled_engines)

        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    searxng = SearXNG()
    results = searxng.search(query="!se google")
    pprint(results)