import time
from ....llm.gemini import GeminiLLM
from langchain_core.documents import Document
from langchain_community.document_loaders import YoutubeLoader
from typing import List, Generator, Any, Optional
from .config import youtube_languages

from .interface import (
    YoutubeNotesPickerRequest,
    SubSectionResponse,
)


class YoutubeVideosNotesPicker:
    def __init__(self) -> None:
        self.loaded_video_docs: List[Document] = []
        self.agent = None

    def _get_splitted_contents(self) -> List[str]:
        return [doc.page_content for doc in self.loaded_video_docs]

    def _generate_notes(self) -> str:
        contents = self._get_splitted_contents()
        notes = []

        for content in contents:
            res = self.agent.run(content)
            notes.append(res.output)
            time.sleep(2)

        raw_notes = f"\n".join(notes)
        return raw_notes

    def run(
        self, data: YoutubeNotesPickerRequest
    ) -> Generator[SubSectionResponse, Any, None]:
        self.agent = GeminiLLM(
            system_prompt=data.system_prompt,
            use_memory=True,
        )

        video_counter = 1
        for youtube_result in data.urls:
            video_docs = (
                YoutubeLoader(
                    video_id=youtube_result.youtube_url,
                    add_video_info=True,
                    language=youtube_languages,
                    translation="en",
                    continue_on_failure=True,
                )
                .from_youtube_url(
                    youtube_result.youtube_url,
                    add_video_info=True,
                )
                .load()
            )

            self.loaded_video_docs.extend(video_docs)

            if youtube_result.title:
                title = youtube_result.title
            else:
                title = f"Video {video_counter:02}"
                video_counter += 1

            notes_content = self._generate_notes()
            raw_content = "\n\n".join(self._get_splitted_contents())
            section_response = SubSectionResponse(
                title=title, content=notes_content, video_url=youtube_result.youtube_url, raw_content=raw_content
            )
            yield section_response
