from __future__ import annotations

from enum import Enum


class HuggingFaceTask(str, Enum):
    SEQUENCE_CLASSIFICATION = "SEQUENCE_CLASSIFICATION"
    TOKEN_CLASSIFICATION = "TOKEN_CLASSIFICATION"
    FILL_MASK = "FILL_MASK"
    TEXT_GENERATION = "TEXT_GENERATION"
    TEXT2TEXT_GENERATION = "TEXT2TEXT_GENERATION"


class Backend(str, Enum):
    AUTO = "AUTO"
    VLLM = "VLLM"
    HUGGINGFACE = "HUGGINGFACE"


class DType(str, Enum):
    AUTO = "AUTO"
    FLOAT32 = "FLOAT32"
    FLOAT16 = "FLOAT16"
    BFLOAT16 = "BFLOAT16"
    FLOAT = "FLOAT"
    HALF = "HALF"
