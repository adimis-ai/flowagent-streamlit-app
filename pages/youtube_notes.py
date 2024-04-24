import streamlit as st
from typing import List
from services.toolkit.service import ToolkitService
from streamlit_player import st_player
from urllib.parse import urlparse, parse_qs
from services.toolkit.tools.youtube_video_notes_picker.interface import (
    YoutubeNotesPickerRequest,
)
from services.toolkit.tools.youtube_search.interface import (
    YoutubeSearchResult,
    YoutubeSearchToolRequest,
)

toolkit_service = ToolkitService()

def extract_video_id(video_url):
    query_string = urlparse(video_url).query
    parameters = parse_qs(query_string)
    video_id = parameters.get('v', [None])[0]
    return video_id

def youtube_notes_generator(
    system_prompt: str, search_query: str, search_results: List[YoutubeSearchResult]
):
    request_data = YoutubeNotesPickerRequest(
        system_prompt=system_prompt,
        query=search_query,
        urls=search_results,
    )
    print("youtube_notes_generator request_data: ", request_data)
    for video_notes in toolkit_service.call_youtube_notes_picker(request_data):
        yield video_notes


def youtube_search(system_prompt: str, query: str, max_results: int):
    request_data = YoutubeSearchToolRequest(
        query=query,
        max_results=max_results,
    )
    youtube_search_results = toolkit_service.call_youtube_search_tool(request_data)
    print("youtube_search_results: ", youtube_search_results)

    if youtube_search_results:
        for notes in youtube_notes_generator(
            system_prompt, query, youtube_search_results
        ):
            print("youtube_notes_generator notes: ", notes)
            yield notes
    else:
        st.error("No videos found or there was an error fetching the videos.")


def youtube_page():
    st.markdown("# Youtube Notes Picker")
    search_type = st.radio(
        "Choose your input type:",
        ("Search YouTube by query", "Enter YouTube video URLs"),
    )

    if search_type == "Search YouTube by query":
        user_query = st.text_input("Enter search query:", "")
        max_results = st.slider("Select max results:", 1, 50, 10)
        system_prompt = st.text_area(
            "Enter system prompt:",
            "You are tasked with transcribing YouTube videos. Convert the provided unstructured transcript into a clear, well-structured, and easily understandable format. Ensure to accurately retain all numerical and statistical data, as well as any quotes or specific lines that are crucial and interesting for my article to make it more realistic.",
        )
        if st.button("Search"):
            st.spinner(text="Fetching videos and generating notes...")
            with st.expander("See results"):
                try:
                    results_generator = youtube_search(
                        system_prompt, user_query, max_results
                    )
                    for notes in results_generator:
                        print("gen notes: ", notes)
                        st.title(notes.title)
                        video_id = extract_video_id(notes.video_url)
                        st_player(f"https://youtu.be/{video_id}")
                        st.markdown(notes.content)
                        st.markdown("---")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
    elif search_type == "Enter YouTube video URLs":
        url_input = st.text_area("Enter YouTube URLs separated by newlines:")
        urls = url_input.split()
        search_results = [YoutubeSearchResult(youtube_url=url) for url in urls]
        if st.button("Generate Notes"):
            st.spinner(text="Generating notes for provided URLs...")
            with st.expander("See results"):
                try:
                    notes_generator = youtube_notes_generator(
                        system_prompt, user_query, search_results
                    )
                    for notes in notes_generator:
                        st.title(notes.title)
                        video_id = extract_video_id(notes.video_url)
                        st_player(f"https://youtu.be/{video_id}")
                        st.markdown(notes.content)
                        st.markdown("---")
                except Exception as e:
                    st.error(f"An error occurred: {e}")


youtube_page()
