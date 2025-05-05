from factory_sdk.dto.resource import (
    FactoryResourceInitData,
    FactoryResourceMeta,
    FactoryResourceRevision,
)
from typing import List
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum
from transformers import AutoModelForCausalLM, AutoProcessor, AutoTokenizer
from PIL import Image
from factory_sdk.utils.image import pil_to_datauri
from typing import Any


class ModelArchitecture(str, Enum):
    Gemma2ForCausalLM = "Gemma2ForCausalLM"
    LlamaForCausalLM = "LlamaForCausalLM"
    MistralForCausalLM = "MistralForCausalLM"
    Phi3ForCausalLM = "Phi3ForCausalLM"
    Qwen2ForCausalLM = "Qwen2ForCausalLM"
    #PaliGemmaForConditionalGeneration = "PaliGemmaForConditionalGeneration"
    Phi3VForCausalLM = "Phi3VForCausalLM"
    Qwen2_5_VLForConditionalGeneration = "Qwen2_5_VLForConditionalGeneration"
    Qwen3ForCausalLM = "Qwen3ForCausalLM"

SUPPORTED_ARCHITECTURES=[
"Qwen2ForCausalLM",
"LlamaForCausalLM",
"Gemma2ForCausalLM",
"Phi3ForCausalLM",
"Phi3VForCausalLM",
"Qwen2_5_VLForConditionalGeneration",
"Qwen3ForCausalLM"
]

ARCH2AUTO = {
    ModelArchitecture.LlamaForCausalLM: AutoModelForCausalLM,
    ModelArchitecture.Qwen2ForCausalLM: AutoModelForCausalLM,
    ModelArchitecture.MistralForCausalLM: AutoModelForCausalLM,
    ModelArchitecture.Gemma2ForCausalLM: AutoModelForCausalLM,
    ModelArchitecture.Phi3ForCausalLM: AutoModelForCausalLM,
    #ModelArchitecture.PaliGemmaForConditionalGeneration: AutoModelForCausalLM,
    ModelArchitecture.Phi3VForCausalLM: AutoModelForCausalLM,
    ModelArchitecture.Qwen3ForCausalLM: AutoModelForCausalLM,
}

ARCH2PROCESSOR = {
    ModelArchitecture.LlamaForCausalLM: AutoTokenizer,
    ModelArchitecture.Qwen2ForCausalLM: AutoTokenizer,
    ModelArchitecture.MistralForCausalLM: AutoTokenizer,
    ModelArchitecture.Gemma2ForCausalLM: AutoTokenizer,
    ModelArchitecture.Phi3ForCausalLM: AutoTokenizer,
    #ModelArchitecture.PaliGemmaForConditionalGeneration: AutoProcessor,
    ModelArchitecture.Phi3VForCausalLM: AutoProcessor,
    ModelArchitecture.Qwen3ForCausalLM: AutoTokenizer,
}


class ModelMeta(FactoryResourceMeta):
    pass


class ModelInitData(FactoryResourceInitData):
    def create_meta(self, tenant_name, project_name=None) -> ModelMeta:
        return ModelMeta(name=self.name, tenant=tenant_name, type="model")


class ModelRevision(FactoryResourceRevision):
    pass


class ModelObject(BaseModel):
    meta: ModelMeta
    revision: str


class InputImage(BaseModel):
    data: str

    @staticmethod
    def from_pil(image: Image) -> "InputImage":
        return InputImage(data=pil_to_datauri(image))


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class Role2Int(Enum):
    SYSTEM = 0
    USER = 1
    ASSISTANT = 2

class Message(BaseModel):
    role: Role
    content: str


class ModelChatInput(BaseModel):
    images: Optional[List[Image.Image]] = None
    messages: List[Message] = Field(min_length=1)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class Token(BaseModel):
    id: int


class GeneratedToken(Token):
    logprob: float
    rank: int


class MetricScore(BaseModel):
    score: float


class ModelInstance(BaseModel):
    model: Any
    processor: Any
    tokenizer: Any
