from enum import Enum


class PretrainedEmbeddingModelName(str, Enum):
    CDE_SMALL = "CDE_SMALL"
    CLIP_BASE = "CLIP_BASE"
    DISTILBERT = "DISTILBERT"
    GTE_BASE = "GTE_BASE"
    GTE_SMALL = "GTE_SMALL"

    def __str__(self) -> str:
        return str(self.value)
