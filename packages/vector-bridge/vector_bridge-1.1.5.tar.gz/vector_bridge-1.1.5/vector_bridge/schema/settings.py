from typing import Dict, List

from pydantic import BaseModel, Field

EXTENSIONS = [
    "txt",
    "csv",
    "xlsx",
    "docx",
    "pdf",
    "rtf",
    "png",
    "jpeg",
    "jpg",
    "webp",
    "mp3",
    "mp4",
    "mpeg",
    "mpga",
    "m4a",
    "wav",
    "webm",
]


MIME_TYPES_EXTENSIONS = {
    "text/csv": [".csv"],
    "text/plain": [".txt"],
    "application/rtf": [".rtf"],
    "application/pdf": [".pdf"],
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    "image/png": [".png"],
    "image/jpg": [".jpeg", ".jpg"],
    "image/webp": [".webp"],
    "audio/mpeg": [".mp3", ".mpga"],
    "video/mp4": [".mp4"],
    "video/mpeg": [".mpeg"],
    "audio/m4a": [".m4a"],
    "audio/wav": [".wav"],
    "video/webm": [".webm"],
    "audio/webm": [".webm"],
}


class PricingUnits(BaseModel):
    unit_price: float
    min_units: int
    free_amount: int
    currency: str = Field(default="USD")


class Pricing(BaseModel):
    request: PricingUnits
    processing_second: PricingUnits
    environments: PricingUnits
    file_storage_gb: PricingUnits
    team_members: PricingUnits


class FilesConfig(BaseModel):
    max_size_bytes: int = Field(default=20000000)
    types: List[str] = Field(default=EXTENSIONS)
    mime_types: Dict[str, List[str]] = Field(default=MIME_TYPES_EXTENSIONS)


class AIModelConfig(BaseModel):
    model: str
    max_tokens: int


OPEN_AI_MODELS = [
    AIModelConfig(model="o1", max_tokens=100000),
    AIModelConfig(model="o1-mini", max_tokens=65536),
    AIModelConfig(model="gpt-4o", max_tokens=16384),
    AIModelConfig(model="gpt-4o-mini", max_tokens=16384),
]


AZURE_OPEN_AI_MODELS = [
    AIModelConfig(model="gpt-4-0125-preview", max_tokens=16384),
    AIModelConfig(model="gpt-4-32k-0613", max_tokens=16384),
]


ANTHROPIC_AI_MODELS = [
    AIModelConfig(model="claude-3-7-sonnet-latest", max_tokens=8192),
    AIModelConfig(model="claude-3-5-sonnet-latest", max_tokens=8192),
    AIModelConfig(model="claude-3-5-haiku-latest", max_tokens=8192),
]


DEEP_SEEK_MODELS = [
    AIModelConfig(model="deepseek-chat", max_tokens=8000),
    AIModelConfig(model="deepseek-reasoner", max_tokens=8000),
]


class MinMax(BaseModel):
    min: float
    max: float


class OpenAIConfig(BaseModel):
    presence_penalty: MinMax = Field(default=MinMax(min=-2.0, max=2.0))
    frequency_penalty: MinMax = Field(default=MinMax(min=-2.0, max=2.0))
    temperature: MinMax = Field(default=MinMax(min=0.0, max=2.0))
    models: List[AIModelConfig] = Field(default=OPEN_AI_MODELS)


class AzureOpenAIConfig(BaseModel):
    presence_penalty: MinMax = Field(default=MinMax(min=-2.0, max=2.0))
    frequency_penalty: MinMax = Field(default=MinMax(min=-2.0, max=2.0))
    temperature: MinMax = Field(default=MinMax(min=0.0, max=2.0))
    models: List[AIModelConfig] = Field(default=AZURE_OPEN_AI_MODELS)


class AnthropicAIConfig(BaseModel):
    temperature: MinMax = Field(default=MinMax(min=0.0, max=1.0))
    models: List[AIModelConfig] = Field(default=ANTHROPIC_AI_MODELS)


class DeepSeekAIConfig(BaseModel):
    presence_penalty: MinMax = Field(default=MinMax(min=-2.0, max=2.0))
    frequency_penalty: MinMax = Field(default=MinMax(min=-2.0, max=2.0))
    temperature: MinMax = Field(default=MinMax(min=0.0, max=2.0))
    models: List[AIModelConfig] = Field(default=DEEP_SEEK_MODELS)


class AIConfig(BaseModel):
    open_ai: OpenAIConfig = Field(default=OpenAIConfig())
    # azure_open_ai: AzureOpenAIConfig = Field(default=AzureOpenAIConfig())
    anthropic: AnthropicAIConfig = Field(default=AnthropicAIConfig())
    deepseek: DeepSeekAIConfig = Field(default=DeepSeekAIConfig())


class Settings(BaseModel):
    files: FilesConfig
    ai: AIConfig
    pricing: Pricing
