from enum import Enum
from typing import List


class VisionLLMModel(str, Enum):
    """Available vision LLM models."""

    LLAMA_4_MAVERICK_17B_INSTRUCT = "us.meta.llama4-maverick-17b-instruct-v1:0"
    LLAMA_4_SCOUT_17B_INSTRUCT = "us.meta.llama4-scout-17b-instruct-v1:0"
    LLAMA_3_2_90B_VISION = "us.meta.llama3-2-90b-instruct-v1:0"
    LLAMA_3_2_11B_VISION = "us.meta.llama3-2-11b-instruct-v1:0"

    @classmethod
    def values(cls) -> List[str]:
        return [e.value for e in cls]

    @classmethod
    def all_models(cls) -> List[str]:
        return cls.values()


class AIModels(str, Enum):
    # Amazon models
    AMAZON_NOVA_PRO = "amazon.nova-pro-v1:0"
    AMAZON_NOVA_LITE = "amazon.nova-lite-v1:0"
    AMAZON_NOVA_MICRO = "amazon.nova-micro-v1:0"

    # Anthropic Models
    CLAUDE_3_7_SONNET = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    CLAUDE_3_5_SONNET_V2 = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    CLAUDE_3_5_SONNET = "us.anthropic.claude-3-5-sonnet-20240620-v1:0"
    CLAUDE_3_5_HAIKU = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
    CLAUDE_3_OPUS = "us.anthropic.claude-3-opus-20240229-v1:0"
    CLAUDE_3_SONNET = "us.anthropic.claude-3-sonnet-20240229-v1:0"
    CLAUDE_3_HAIKU = "us.anthropic.claude-3-haiku-20240307-v1:0"

    # Cohere Models
    COHERE_COMMAND_R_PLUS_V3 = "cohere/command-r-plus-08-2024"
    COHERE_COMMAND_R_PLUS_V2 = "cohere/command-r-plus-04-2024"
    COHERE_COMMAND_PLUS = "cohere.command-r-plus-v1:0"
    COHERE_COMMAND_R_V3 = "cohere/command-r-08-2024"
    COHERE_COMMAND_R_V2 = "cohere/command-r-03-2024"
    COHERE_COMMAND_R = "cohere.command-r-v1:0"
    COHERE_COMMAND_LIGHT = "cohere.command-light-text-v14"

    # Deepseek Models
    DEEPSEEK_R1_V1 = "us.deepseek.r1-v1:0"

    # Meta Models
    LLAMA_4_MAVERICK_17B_INSTRUCT = "us.meta.llama4-maverick-17b-instruct-v1:0"
    LLAMA_4_SCOUT_17B_INSTRUCT = "us.meta.llama4-scout-17b-instruct-v1:0"
    LLAMA_3_3_70B_INSTRUCT = "meta.llama3-3-70b-instruct-v1:0"
    LLAMA_3_2_90B_VISION = "us.meta.llama3-2-90b-instruct-v1:0"
    LLAMA_3_2_11B_VISION = "us.meta.llama3-2-11b-instruct-v1:0"
    LLAMA_3_2_1B_INSTRUCT = "us.meta.llama3-2-1b-instruct-v1:0"
    LLAMA_3_1_70B_INSTRUCT = "us.meta.llama3-1-70b-instruct-v1:0"
    LLAMA_3_1_8B_INSTRUCT = "us.meta.llama3-1-8b-instruct-v1:0"


class QueryMode(str, Enum):
    DEFAULT = "default"
    SPARSE = "sparse"
    HYBRID = "hybrid"
    TEXT_SEARCH = "text_search"
    SEMANTIC_HYBRID = "semantic_hybrid"

    # fit learners
    SVM = "svm"
    LOGISTIC_REGRESSION = "logistic_regression"
    LINEAR_REGRESSION = "linear_regression"

    # maximum marginal relevance
    MMR = "mmr"


class ImageFileExtensions(str, Enum):
    JPG = ".jpg"
    JPEG = ".jpeg"
    PNG = ".png"
    GIF = ".gif"
    BMP = ".bmp"
    TIFF = ".tiff"
    ICO = ".ico"
    WEBP = ".webp"

    @classmethod
    def values(cls) -> List[str]:
        return [e.value for e in cls]


class VideoFileExtensions(str, Enum):
    MP4 = ".mp4"
    AVI = ".avi"
    MOV = ".mov"
    WMV = ".wmv"
    FLV = ".flv"
    MPEG = ".mpeg"
    MPG = ".mpg"
    M4V = ".m4v"
    WEBM = ".webm"
    MKV = ".mkv"

    @classmethod
    def values(cls) -> List[str]:
        return [e.value for e in cls]
