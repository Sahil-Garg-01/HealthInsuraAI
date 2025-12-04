"""
Application settings and configuration.

Centralizes all configuration with environment variable support.
"""

import os
from dataclasses import dataclass, field
from typing import Dict
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class APIEndpoints:
    """Hugging Face API endpoints."""
    ner: str = os.getenv("HF_NER_URL")
    classify: str = os.getenv("HF_CLASSIFY_URL")
    summarize: str = os.getenv("HF_SUMMARIZE_URL")
    describe_image: str = os.getenv("HF_DESCRIBE_URL")
    signature: str = os.getenv("HF_SIGNATURE_URL")
    stamp: str = os.getenv("HF_STAMP_URL")
    extract_text: str = os.getenv("HF_TEXT_URL")
    extract_tables: str = os.getenv("HF_TABLES_URL")
    translate: str = os.getenv("HF_TRANSLATE_URL")


@dataclass(frozen=True)
class LLMSettings:
    """LLM configuration."""
    model: str = os.getenv("LLM_MODEL", "gpt-4")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0"))
    api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))


@dataclass(frozen=True)
class ProcessingSettings:
    """Document processing settings."""
    language: str = os.getenv("PROCESSING_LANGUAGE", "en")
    default_start_page: int = 1
    default_end_page: int = 10


@dataclass(frozen=True)
class Settings:
    """Main settings container."""
    api: APIEndpoints = field(default_factory=APIEndpoints)
    llm: LLMSettings = field(default_factory=LLMSettings)
    processing: ProcessingSettings = field(default_factory=ProcessingSettings)


# Global settings instance
settings = Settings()
