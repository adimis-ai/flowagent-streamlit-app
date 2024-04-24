from typing import List, Generator, Any, Optional
from .tools.youtube_search.index import YoutubeSearchTool
from .tools.youtube_video_notes_picker.index import YoutubeVideosNotesPicker

from .tools.youtube_video_notes_picker.interface import (
    YoutubeNotesPickerRequest,
    SubSectionResponse,
)
from .tools.youtube_search.interface import (
    YoutubeSearchResult,
    YoutubeSearchToolRequest,
)


class ToolkitService:
    def __init__(self):
        pass

    def call_youtube_search_tool(
        self,
        data: YoutubeSearchToolRequest,
    ) -> List[YoutubeSearchResult]:
        return YoutubeSearchTool().run(data.query, data.max_results)

    def call_youtube_notes_picker(
        self,
        data: YoutubeNotesPickerRequest,
    ) -> Generator[SubSectionResponse, Any, None]:
        picker = YoutubeVideosNotesPicker()

        for response in picker.run(data):
            yield response
