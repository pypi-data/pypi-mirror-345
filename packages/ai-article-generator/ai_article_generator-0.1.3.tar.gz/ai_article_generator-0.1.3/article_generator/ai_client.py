import os

import httpx
import openai
from dotenv import load_dotenv

load_dotenv()

DEFAULT_SYSTEM_PROMPTS = {
    "review": (
        "You are an expert reviewer and SEO specialist generating structured, insightful, and engaging review content. "
        "Ensure the writing is optimized for search engines: use relevant keywords naturally, write clear meta descriptions, "
        "and structure content for readability and user engagement."
    ),
    "news": (
        "You are a professional journalist and SEO expert writing clear, concise, and factual news articles. "
        "Optimize for search engines by using relevant keywords, concise headlines, and structured content."
    ),
    "guide": (
        "You are an expert educator and SEO specialist writing step-by-step guides for beginners. "
        "Ensure the guide is optimized for search engines: use clear headings, relevant keywords, and actionable steps."
    ),
    "feature": (
        "You are a creative writer and SEO expert crafting in-depth feature articles. "
        "Write engaging, well-structured content that is optimized for search engines and user engagement."
    ),
    "generic": (
        "You are a helpful and knowledgeable content writer with strong SEO skills. "
        "Write clear, engaging, and search-optimized content."
    ),
}


class AIClient:
    def __init__(self, article_type: str = "generic", system_prompt: str = None, model: str = "gpt-4o-mini"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPTS.get(
            article_type, DEFAULT_SYSTEM_PROMPTS["generic"]
        )
        http_client = httpx.Client()
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"), http_client=http_client)
        self.model = model
    def generate(self, prompt: str, system_prompt: str = None, **kwargs):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=messages,
            **{k: v for k, v in kwargs.items()},
        )
        return response.choices[0].message.content
