import os
import time
import random
from typing import List, Optional
import google.generativeai as genai
from .interface import GeminiLLMToolResponse
import tiktoken


class GeminiLLM:
    def __init__(
        self,
        system_prompt: str,
        api_key: Optional[str] = os.getenv("GOOGLE_API_KEY"),
        model: str = "gemini-1.0-pro",
        use_memory: bool = True,
        max_retries: int = 100,
        temperature: float = 0.0,
        top_p: float = 1.0,
        top_k: int = 1,
        max_output_tokens: int = 2048,
        safety_settings: List[dict] = [],
    ):
        genai.configure(api_key=api_key)
        self.system_prompt = system_prompt
        self.model = genai.GenerativeModel(
            model_name=model,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
                "top_p": top_p,
                "top_k": top_k,
            },
            safety_settings=safety_settings,
        )
        self.max_retries = max_retries
        self.chat_history: List[dict] = []
        self.use_memory = use_memory
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def _call_llm(self, input_str: str, refresh_chats: bool = False):
        retries = 0

        if refresh_chats:
            self.chat_history = []

        while retries < self.max_retries:
            try:
                chat_history_str = "\n".join(
                    [
                        f"{entry['role']}: {entry['content']}"
                        for entry in self.chat_history
                    ]
                )
                print("=" * 80)
                prompt_parts = [
                    f"System Prompt: {self.system_prompt}",
                    *([f"Chat History: {chat_history_str}"] if self.use_memory else []),
                    f"User Message: {input_str}",
                ]
                print("Final Prompt: ", prompt_parts)
                response = self.model.generate_content(prompt_parts)

                if self.use_memory:
                    self.chat_history.append({"role": "user", "content": input_str})
                    self.chat_history.append({"role": "assistant", "content": response})

                return {
                    "input": input_str,
                    "output": response.text,
                }
            except Exception as e:
                print(f"Error: {e}")
                retries += 1
                print(f"Retry {retries}/{self.max_retries}")
                delay_seconds = random.uniform(5, 15)
                print(f"Waiting for {delay_seconds:.2f} seconds before retrying...")
                time.sleep(delay_seconds)
        raise Exception(f"All {self.max_retries} retries failed. Last error: {e}")

    def _count_tokens(self, text: str) -> int:
        print("Counting Token...", text)
        response = len(self.encoding.encode(text))
        return int(response)

    def run(self, input_str: str, refresh_chats: bool = False) -> GeminiLLMToolResponse:
        try:
            start_time = time.time()
            response = self._call_llm(input_str, refresh_chats)
            end_time = time.time()
            token_count = self._count_tokens(response["output"])
            time_taken = int(end_time - start_time)
            print("Time Taken:", time_taken)
            print("Tokens:", token_count)
            response = GeminiLLMToolResponse(
                input=response["input"],
                output=response["output"],
                response_token=token_count,
                time_taken=time_taken,
            )

            print("Gemini Response:", response)
            return response
        except Exception as e:
            print(f"Error: {e}")
