from typing import Optional
from pydantic import BaseModel


class YoutubeSearchResult(BaseModel):
    youtube_url: str
    title: Optional[str]
    long_desc: Optional[str]
    channel: Optional[str]
    duration: Optional[str]
    views: Optional[str]
    publish_time: Optional[str]
    url_suffix: Optional[str]


class YoutubeSearchToolRequest(BaseModel):
    query: str
    max_results: int = 10
