import re
from typing import List
from youtube_search import YoutubeSearch
from .interface import YoutubeSearchResult


class YoutubeSearchTool:
    def __init__(self) -> None:
        pass

    def _parse_results(self, results: List[dict]) -> List[YoutubeSearchResult]:
        url_prefix = "https://www.youtube.com/"
        if isinstance(results, list):
            videos = results
        elif isinstance(results, dict) and "videos" in results:
            videos = results["videos"]
        else:
            raise ValueError("Invalid search results format")
        sorted_results = sorted(
            videos,
            key=lambda x: (int(x["views"].split()[0].replace(",", "")),),
            reverse=True,
        )
        parsed_results = [
            YoutubeSearchResult(
                title=video["title"],
                youtube_url=url_prefix + video["url_suffix"],
                long_desc=video["long_desc"],
                channel=video["channel"],
                duration=video["duration"],
                views=video["views"],
                publish_time=video.get("publish_time", None),
                url_suffix=video["url_suffix"],
            )
            for video in sorted_results
        ]
        pattern = re.compile(r"\b(?:year|years)\b", flags=re.IGNORECASE)
        parsed_results = [
            result
            for result in parsed_results
            if "publish_time" in result.dict()
            and not pattern.search(result.dict()["publish_time"])
        ]
        return parsed_results

    def run(self, query: str, max_results: int) -> List[YoutubeSearchResult]:
        results = YoutubeSearch(query, max_results=max_results).to_dict()
        return self._parse_results(results=results)
