import logging

from .ai_client import AIClient
from .exceptions import ArticleGenerationError
from .section import SectionFactory


class ArticleGenerator:
    ALLOWED_ARTICLE_TYPES = ("review", "news", "guide", "feature", "generic")

    def __init__(
        self,
        instructions: dict,
        additional_data: dict = None,
        article_type: str = "generic",
        system_prompt: str = None,
        model: str = "gpt-4o-mini",
    ):
        if article_type not in self.ALLOWED_ARTICLE_TYPES:
            raise ValueError(
                f"Invalid article type: {article_type}. Must be one of: {', '.join(self.ALLOWED_ARTICLE_TYPES)}"
            )
        self.instructions = instructions
        self.data = additional_data
        self.logger = logging.getLogger("ArticleGenerator")
        self.ai_client = AIClient(article_type, system_prompt, model)
        self.section_factory = SectionFactory(self.ai_client)
        self.article_type = article_type
        self.model = model

    def generate(self) -> dict:
        html_sections = {}
        for section_name, section_info in self.instructions.items():
            try:
                section = self.section_factory.create(section_name, section_info, self.data)
                html = section.generate_html()
                html_sections[section_name] = html
            except Exception as e:
                self.logger.error(f"Failed to generate section '{section_name}': {e}")
                raise ArticleGenerationError(f"Section '{section_name}' failed") from e
        return html_sections
