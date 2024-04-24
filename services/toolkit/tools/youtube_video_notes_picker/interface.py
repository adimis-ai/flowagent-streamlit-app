from pydantic import BaseModel
from typing import List, Optional
from ..youtube_search.interface import YoutubeSearchResult


class SubSectionResponse(BaseModel):
    title: str
    content: Optional[str]
    video_url: Optional[str]


class YoutubeNotesPickerRequest(BaseModel):
    system_prompt: str
    query: str
    urls: List[YoutubeSearchResult]


class YoutubeNotesPickerResponse(BaseModel):
    dictionary: List[SubSectionResponse]
    raw_string: str
