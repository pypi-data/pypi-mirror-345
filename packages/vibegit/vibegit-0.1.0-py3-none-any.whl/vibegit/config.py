from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic_settings import BaseSettings

from vibegit.git import GitContextFormatter


class ContextFormattingConfig(BaseSettings):
    include_active_branch: bool = True
    truncate_lines: int | None = None
    include_latest_commits: int | None = 5

    def get_context_formatter(self, user_instructions: str | None = None) -> GitContextFormatter:
        return GitContextFormatter(
            include_active_branch=self.include_active_branch,
            truncate_lines=self.truncate_lines,
            include_latest_commits=self.include_latest_commits,
            user_instructions=user_instructions,
        )


class Config(BaseSettings):
    model_name: str = "google_genai:gemini-2.5-flash-preview-04-17"
    context_formatting: ContextFormattingConfig = ContextFormattingConfig()

    def get_chat_model(self) -> BaseChatModel:
        return init_chat_model(self.model_name)
